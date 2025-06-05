"""
llm_prompt_scorer.py

Purpose : Scores prompts using a language model (LLM) and a defined scoring matrix.
Logging : Logs all events (including errors) into a centralized workflow JSONL log using JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Every scoring run (success or error) is appended as an AgentEvent to the workflow log.
# - No per-run or per-agent scattered files, only compliant JSONL logging per workflow/session.
# - Scalable and fully traceable for auditing, debugging, and analytics.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient


class LLMPromptScorer:
    def __init__(
        self,
        scoring_matrix: dict,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        """
        scoring_matrix: dict or object with scoring logic
        openai_client: injected LLM client
        log_dir: directory for workflow logs (default: logs/workflows)
        """
        self.scoring_matrix = scoring_matrix
        self.llm = openai_client
        self.log_dir = log_dir

    def _calculate_score(self, llm_result: str) -> float:
        """
        Calculates a numeric score based on the presence of positive and negative keywords defined
        in the scoring matrix.

        Returns a float between 0 and 1.
        """
        score = 0.0
        total_weight = 0.0

        # Score positive keywords
        for kw in self.scoring_matrix.get("keywords", []):
            if kw.lower() in llm_result.lower():
                score += self.scoring_matrix["weights"].get("keywords", 0.0)
            total_weight += abs(self.scoring_matrix["weights"].get("keywords", 0.0))

        # Deduct score for negative keywords
        for nkw in self.scoring_matrix.get("negative_keywords", []):
            if nkw.lower() in llm_result.lower():
                score += self.scoring_matrix["weights"].get("negative_keywords", 0.0)
            total_weight += abs(
                self.scoring_matrix["weights"].get("negative_keywords", 0.0)
            )

        if total_weight == 0:
            return 0.0

        final_score = max(0.0, min(1.0, score / total_weight))
        return final_score

    def _extract_feedback(self, llm_output: str) -> str:
        """
        Simple example method to extract dynamic feedback from the LLM output text.
        You can extend this with NLP parsing, keyword extraction, or structured prompts.
        """
        # For demo: return a short snippet or summary from the output
        if len(llm_output) > 200:
            return llm_output[:200] + "..."
        return llm_output

    def run(
        self, prompt_path: Path, base_name: str, iteration: int, workflow_id: str = None
    ):
        """
        Scores a prompt by sending it to the LLM and evaluating the response using the scoring matrix.
        Logs the entire process as an AgentEvent in a centralized JSONL workflow log.
        """
        if workflow_id is None:
            workflow_id = f"{datetime.utcnow().isoformat(timespec='seconds').replace(':', '-')}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # Read prompt content
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()

            # Get LLM response
            llm_response = self.llm.chat_completion(prompt=prompt_content)
            llm_output = (
                llm_response.choices[0].message.get("content", "")
                if llm_response.choices
                else ""
            )

            # Calculate score and determine pass/fail
            score = self._calculate_score(llm_output)
            pass_threshold = score >= self.scoring_matrix.get("threshold", 0.5)

            # Extract dynamic, context-sensitive feedback
            feedback = self._extract_feedback(llm_output)

            # Prepare event payload
            payload = {
                "llm_output": llm_output,
                "score": score,
                "pass_threshold": pass_threshold,
                "feedback": feedback,
            }

            # Log success event
            event = AgentEvent(
                event_type="llm_prompt_score",
                agent_name="LLMPromptScorer",
                agent_version="1.1.0",
                timestamp=datetime.utcnow(),
                step_id="scoring",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "scoring_matrix": str(self.scoring_matrix),
                },
            )
            logger.log_event(event)
            return event

        except Exception as ex:
            import traceback

            # Log error event
            error_event = AgentEvent(
                event_type="error",
                agent_name="LLMPromptScorer",
                agent_version="1.1.0",
                timestamp=datetime.utcnow(),
                step_id="scoring",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                    "scoring_matrix": str(self.scoring_matrix),
                },
            )
            logger.log_event(error_event)
            raise
