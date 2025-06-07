"""
prompt_quality_agent.py

Purpose : Evaluates prompt quality using a scoring matrix and integrates LLMPromptScorer for scoring.
Logging : Logs all events (success and error) into a centralized JSONL workflow log via JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Delegates scoring to LLMPromptScorer to maintain single source of truth for scoring logic.
# - Maintains centralized workflow JSONL logging for traceability.
# - Logs all agent actions and errors as structured AgentEvents.
# - Designed for scalable, auditable prompt quality evaluation.
# - Optionally triggers LLM-based detailed feedback generation per placeholder using scoring matrix context.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4
import re

from utils.time_utils import cet_now, timestamp_for_filename
from utils.openai_client import OpenAIClient
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.scoring_matrix_loader import load_scoring_matrix
from utils.scoring_matrix_types import ScoringMatrixType
from agents.llm_prompt_scorer import LLMPromptScorer


class PromptQualityAgent:
    def __init__(
        self,
        scoring_matrix_type,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        """
        scoring_matrix_type: Enum value defining which scoring matrix to load
        openai_client: injected OpenAIClient instance
        log_dir: directory for workflow logs (default: logs/workflows)
        """
        self.scoring_matrix_type = scoring_matrix_type
        self.scoring_matrix = load_scoring_matrix(scoring_matrix_type)
        self.llm = openai_client
        self.log_dir = log_dir
        self.scorer = LLMPromptScorer(
            self.scoring_matrix,
            self.llm,
            log_dir=self.log_dir,
        )

    def _generate_llm_detailed_feedback(self, placeholders, prompt_text):
        """
        For each placeholder in the prompt, ask the LLM to evaluate
        its semantic quality and compliance with scoring matrix expectations.
        Returns a list of {position, feedback} dicts.
        """
        results = []
        for ph in placeholders:
            criteria = self.scoring_matrix.get(ph, "Keine spezifische Regel vorhanden.")
            prompt = f"""
Du bist ein Prompt-Qualitätsbewerter. Analysiere die folgende Platzhalter-Position im gegebenen Prompt.

Prompt:
{prompt_text}

Platzhalter: {{{ph}}}
Matrix-Anforderung: {criteria}

Beurteile, ob die Position semantisch sinnvoll und regelkonform ist. Gib eine Begründung und eine Verbesserungsempfehlung.
Antworte im Format:
- Bewertung:
- Empfehlung:
"""
            try:
                response = (
                    self.llm.chat_completion(
                        prompt=prompt,
                        temperature=0.3,
                        max_tokens=300,
                    )
                    .choices[0]
                    .message.get("content", "")
                    .strip()
                )
            except Exception as ex:
                response = f"Fehler bei LLM-Auswertung: {ex}"
            results.append({"position": ph, "feedback": response.strip()})
        return results

    def run(
        self,
        prompt_path: Path,
        base_name: str,
        iteration: int,
        workflow_id: str = None,
        detailed_feedback: bool = False,
    ):
        """
        Runs the prompt quality evaluation by delegating to LLMPromptScorer.
        Logs events under the workflow JSONL log.
        Ensures structured feedback (list) for downstream improvement agent.
        If ``detailed_feedback`` is True, additional placeholder-level
        feedback is returned under ``payload['detailed_feedback']``.
        """
        if workflow_id is None:
            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()

            placeholders = re.findall(r"{([^{}]+)}", prompt_content)

            scorer_event = self.scorer.run(
                prompt_path, base_name, iteration, workflow_id
            )
            if scorer_event is None:
                return None

            payload = {
                "criteria_scores": scorer_event.payload.get("criteria_scores"),
                "weighted_score": scorer_event.payload.get("weighted_score"),
                "matrix_feedback": scorer_event.payload.get("matrix_feedback"),
            }

            if detailed_feedback:
                detailed_feedback_llm = self._generate_llm_detailed_feedback(
                    placeholders, prompt_content
                )
                payload["detailed_feedback"] = detailed_feedback_llm

            event = AgentEvent(
                event_type="quality_check",
                agent_name="PromptQualityAgent",
                agent_version="1.7.0",
                timestamp=cet_now(),
                step_id="quality_evaluation",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "scoring_matrix_type": str(self.scoring_matrix_type),
                },
            )

            logger.log_event(event)
            return event

        except Exception as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="PromptQualityAgent",
                agent_version="1.7.0",
                timestamp=cet_now(),
                step_id="quality_evaluation",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                    "scoring_matrix_type": str(self.scoring_matrix_type),
                },
            )
            logger.log_event(error_event)
            raise
