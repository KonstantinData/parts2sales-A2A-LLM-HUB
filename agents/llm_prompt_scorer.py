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
        scoring_matrix,
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

    def run(
        self, prompt_path: Path, base_name: str, iteration: int, workflow_id: str = None
    ):
        """
        Scores a prompt using LLM and the scoring matrix. Logs all actions and errors to workflow JSONL log.
        """
        if workflow_id is None:
            workflow_id = f"{datetime.utcnow().isoformat(timespec='seconds').replace(':', '-')}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # --- Read prompt content
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()

            # --- Score using LLM and matrix (you can expand this logic as needed)
            llm_result = self.llm.chat_completion(prompt=prompt_content)
            score = self._calculate_score(llm_result, self.scoring_matrix)

            payload = {
                "llm_output": llm_result,
                "score": score,
                "matrix_used": str(self.scoring_matrix),
                "feedback": "",
            }

            event = AgentEvent(
                event_type="llm_prompt_score",
                agent_name="LLMPromptScorer",
                agent_version="1.0.0",
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

            error_event = AgentEvent(
                event_type="error",
                agent_name="LLMPromptScorer",
                agent_version="1.0.0",
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

    def _calculate_score(self, llm_result, scoring_matrix):
        """
        Your scoring logic goes here.
        Replace this with your own evaluation rules.
        """
        # Example: return dummy score for now
        return 1.0
