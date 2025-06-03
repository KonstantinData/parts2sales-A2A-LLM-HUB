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

from utils.openai_client import OpenAIClient
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.scoring_matrix_loader import load_scoring_matrix
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
            self.scoring_matrix, self.llm, log_dir=self.log_dir
        )

    def run(
        self, prompt_path: Path, base_name: str, iteration: int, workflow_id: str = None
    ):
        """
        Runs the prompt quality evaluation by delegating to LLMPromptScorer.
        Logs events under the workflow JSONL log.
        """
        if workflow_id is None:
            workflow_id = f"{datetime.utcnow().isoformat(timespec='seconds').replace(':', '-')}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # Delegate scoring to LLMPromptScorer
            score_event = self.scorer.run(
                prompt_path, base_name, iteration, workflow_id
            )

            # Enrich the event if needed or just return it
            logger.log_event(score_event)
            return score_event

        except Exception as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="PromptQualityAgent",
                agent_version="1.4.0",
                timestamp=datetime.utcnow(),
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
