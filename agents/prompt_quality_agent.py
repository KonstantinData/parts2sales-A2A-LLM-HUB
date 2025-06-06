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
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

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
        # Instantiate scorers for deterministic matrix evaluation and
        # optional LLM-based validation. The deterministic scorer does not
        # require an OpenAI client.
        self.matrix_scorer = LLMPromptScorer(
            self.scoring_matrix,
            self.llm,
            log_dir=self.log_dir,
            use_llm=True,
        )

        self.llm_scorer = LLMPromptScorer(
            self.scoring_matrix,
            self.llm,
            log_dir=self.log_dir,
            use_llm=True,
        )

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

            import re
            placeholders = re.findall(r"{([^{}]+)}", prompt_content)

            # Run deterministic matrix scoring
            matrix_event = self.matrix_scorer.run(
                prompt_path, base_name, iteration, workflow_id
            )

            matrix_feedback = matrix_event.payload.get("feedback", [])
            if isinstance(matrix_feedback, str):
                matrix_feedback = [
                    line for line in matrix_feedback.split("\n") if line.strip()
                ]
            if not matrix_feedback:
                matrix_feedback = []

            # Run LLM-based scoring
            llm_event = self.llm_scorer.run(
                prompt_path, base_name, iteration, workflow_id
            )

            llm_feedback = llm_event.payload.get("feedback", [])
            if isinstance(llm_feedback, str):
                llm_feedback = [
                    line for line in llm_feedback.split("\n") if line.strip()
                ]
            if not llm_feedback:
                llm_feedback = []

            detailed_feedback_list = []
            if detailed_feedback:
                combined_matrix = "\n".join(matrix_feedback)
                combined_llm = "\n".join(llm_feedback)
                for ph in placeholders:
                    detailed_feedback_list.append(
                        {
                            "position": ph,
                            "matrix_feedback": combined_matrix,
                            "llm_feedback": combined_llm,
                        }
                    )

            payload = {
                "matrix_score": matrix_event.payload.get("score"),
                "matrix_pass_threshold": matrix_event.payload.get("pass_threshold"),
                "passed_matrix": matrix_event.payload.get("passed"),
                "matrix_results": matrix_event.payload.get("criteria_results"),
                "matrix_feedback": matrix_feedback,
                "llm_score": llm_event.payload.get("score"),
                "llm_pass_threshold": llm_event.payload.get("pass_threshold"),
                "passed_llm": llm_event.payload.get("passed"),
                "llm_results": llm_event.payload.get("criteria_results"),
                "llm_feedback": llm_feedback,
            }
            if detailed_feedback:
                payload["detailed_feedback"] = detailed_feedback_list

            event = AgentEvent(
                event_type="quality_check",
                agent_name="PromptQualityAgent",
                agent_version="1.6.0",
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
                agent_version="1.6.0",
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
