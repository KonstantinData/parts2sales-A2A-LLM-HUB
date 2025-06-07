"""
llm_prompt_scorer.py

Purpose : Scores prompts using a defined scoring matrix.
Logging : Logs all events (including errors) into a centralized workflow JSONL log using JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Uses the LLM to validate each criterion in the scoring matrix.
# - Event log payload only contains the LLM-derived results per criterion.
"""

from pathlib import Path
from uuid import uuid4

from utils.time_utils import cet_now, timestamp_for_filename
from openai import OpenAIError

from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient
from typing import Optional
import re
from config.scoring.raw_scoring_matrix import compute_weighted_score


class LLMUnavailableError(Exception):
    """Raised when the LLM API cannot be reached."""


class LLMPromptScorer:
    def __init__(
        self,
        scoring_matrix: dict,
        openai_client: Optional[OpenAIClient] = None,
        log_dir=Path("logs/workflows"),
    ):
        """
        scoring_matrix: dict with per-criterion descriptions and feedbacks
        openai_client: injected LLM client
        log_dir: directory for workflow logs (default: logs/workflows)
        """
        self.scoring_matrix = scoring_matrix
        self.llm = openai_client
        self.log_dir = log_dir

    def _evaluate_criteria(
        self,
        prompt_content: str,
        logger: JsonlEventLogger,
        base_name: str,
        iteration: int,
    ) -> tuple[dict, list]:
        """
        Evaluates all criteria from the scoring matrix against the prompt content.
        Returns a tuple: (scores dict, matrix feedback list)
        """
        results = {}
        matrix_feedback: list[str] = []

        for key, rule in self.scoring_matrix.items():
            if self.llm is None:
                raise LLMUnavailableError("LLM client not provided")

            llm_score_prompt = rule.get("llm_score")
            description = rule.get("description", "")
            if llm_score_prompt:
                prompt = (
                    f"{llm_score_prompt}\n\nPrompt:\n{prompt_content}\n"
                    "Answer with a single number between 0 and 1."
                )
            else:
                prompt = (
                    f"On a scale from 0 to 1, rate the following criterion:\n{description}\n\n"
                    f"Prompt:\n{prompt_content}\nAnswer with a single number between 0 and 1."
                )

            response = self.llm.chat_completion(
                prompt=prompt,
                temperature=0.0,
                max_tokens=10,
            )

            answer = response.choices[0].message.get("content", "").strip()
            match = re.search(r"([01](?:\.\d+)?)", answer)
            try:
                score = float(match.group(1)) if match else float(answer)
            except (ValueError, AttributeError):
                score = 0.0
            score = max(0.0, min(1.0, score))
            results[key] = score

            if rule.get("feedback"):
                matrix_feedback.append({"criterion": key, "feedback": rule["feedback"]})

        return results, matrix_feedback

    def run(
        self, prompt_path: Path, base_name: str, iteration: int, workflow_id: str = None
    ):
        """
        Scores a prompt by evaluating all matrix criteria via the LLM.
        Logs the entire process as an AgentEvent in a centralized JSONL workflow log.
        """
        if workflow_id is None:
            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # Read prompt content
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()

            # Evaluate criteria
            criteria_scores, matrix_feedback = self._evaluate_criteria(
                prompt_content, logger, base_name, iteration
            )

            weighted_score = compute_weighted_score(criteria_scores)

            payload = {
                "criteria_scores": criteria_scores,
                "weighted_score": weighted_score,
                "matrix_feedback": matrix_feedback,
            }

            event = AgentEvent(
                event_type="llm_prompt_score",
                agent_name="LLMPromptScorer",
                agent_version="2.2.0",
                timestamp=cet_now(),
                step_id="scoring",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "scoring_matrix_keys": list(self.scoring_matrix.keys()),
                },
            )
            logger.log_event(event)
            return event

        except OpenAIError:
            error_event = AgentEvent(
                event_type="error",
                agent_name="LLMPromptScorer",
                agent_version="2.2.0",
                timestamp=cet_now(),
                step_id="scoring",
                prompt_version=base_name,
                status="error",
                payload={"reason": "LLM API unavailable"},
                meta={
                    "iteration": iteration,
                    "scoring_matrix_keys": list(self.scoring_matrix.keys()),
                },
            )
            logger.log_event(error_event)
            return None
        except LLMUnavailableError:
            # Error already logged in _evaluate_criteria
            return None
        except Exception as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="LLMPromptScorer",
                agent_version="2.2.0",
                timestamp=cet_now(),
                step_id="scoring",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                    "scoring_matrix_keys": list(self.scoring_matrix.keys()),
                },
            )
            logger.log_event(error_event)
            raise
