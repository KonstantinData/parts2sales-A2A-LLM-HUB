"""
llm_prompt_scorer.py

Purpose : Scores prompts using a defined scoring matrix.
Logging : Logs all events (including errors) into a centralized workflow JSONL log using JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Implements true weighted, normalized scoring per matrix.
# - Event log always includes: criteria_results, score, pass_threshold, passed, feedback.
# - To extend for LLM-based checks, replace the validation logic pro Kriterium.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from utils.time_utils import cet_now, timestamp_for_filename

from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient
from typing import Optional


class LLMPromptScorer:
    def __init__(
        self,
        scoring_matrix: dict,
        openai_client: Optional[OpenAIClient] = None,
        log_dir=Path("logs/workflows"),
        use_llm: bool = False,
    ):
        """
        scoring_matrix: dict with per-criterion weights, descriptions, and feedbacks
        openai_client: injected LLM client (not required for base matrix scoring)
        log_dir: directory for workflow logs (default: logs/workflows)
        use_llm: if True, criteria are validated via the injected LLM
        """
        self.scoring_matrix = scoring_matrix
        self.llm = openai_client
        self.log_dir = log_dir
        self.use_llm = use_llm

    def _evaluate_criteria(self, prompt_content: str) -> dict:
        """
        Evaluates all criteria from the scoring matrix against the prompt content.
        Returns a dict: {criterion: bool}
        Criteria-Check:
          - If a 'required_snippet' exists, checks for exact presence (case-insensitive).
          - If not, returns True (or implement real logic per Kriterium).
        """
        results = {}
        for key, rule in self.scoring_matrix.items():
            if self.use_llm:
                if self.llm is None:
                    results[key] = False
                    continue
                description = rule.get("description", "")
                prompt = (
                    "Does the following prompt meet this criterion?\n"
                    f"Criterion: {description}\n"
                    "Answer only with 'PASS' or 'FAIL'.\n\n"
                    f"Prompt:\n{prompt_content}"
                )
                try:
                    response = self.llm.chat_completion(
                        prompt=prompt,
                        temperature=0.0,
                        max_tokens=5,
                    )
                    answer = response.choices[0].message.get("content", "").strip().lower()
                    results[key] = answer.startswith("pass")
                except Exception:
                    results[key] = False
            else:
                snippet = rule.get("required_snippet")
                if snippet:
                    results[key] = snippet.lower() in prompt_content.lower()
                else:
                    results[key] = True
        return results

    def _weighted_score(self, results: dict) -> float:
        """
        Calculates the weighted, normalized score for all criteria.
        """
        sum_fulfilled = sum(
            self.scoring_matrix[k]["weight"] for k, v in results.items() if v
        )
        sum_total = sum(v["weight"] for v in self.scoring_matrix.values())
        return sum_fulfilled / sum_total if sum_total > 0 else 0.0

    def run(
        self, prompt_path: Path, base_name: str, iteration: int, workflow_id: str = None
    ):
        """
        Scores a prompt by evaluating all matrix criteria and aggregating weighted score.
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
            criteria_results = self._evaluate_criteria(prompt_content)

            # Calculate weighted, normalized score
            score = self._weighted_score(criteria_results)
            threshold = 0.9  # Set globally or via config/env

            passed = score >= threshold

            # Feedback: collect all feedbacks for unmet criteria
            feedback = [
                self.scoring_matrix[k]["feedback"]
                for k, v in criteria_results.items()
                if not v
            ]

            payload = {
                "criteria_results": criteria_results,
                "score": score,
                "pass_threshold": threshold,
                "passed": passed,
                "feedback": feedback,
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
