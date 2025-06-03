"""
prompt_quality_agent.py

Purpose : Evaluates prompt quality using a scoring matrix and LLM.
Logging : Logs all events (success and error) into a central JSONL workflow log via JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Uses centralized workflow-based JSONL logging for full traceability.
# - All agent actions (including errors) are recorded as structured AgentEvents.
# - No legacy file output or per-agent logging – everything is logged per workflow/session.
# - Ready for scalable, compliant operations and future monitoring.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from utils.openai_client import OpenAIClient
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger


class PromptQualityAgent:
    def __init__(
        self,
        scoring_matrix_type,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        """
        scoring_matrix_type: defines the scoring logic (should match your ScoringMatrixType setup)
        openai_client: injected OpenAIClient instance
        log_dir: base directory for workflow logs (default: logs/workflows)
        """
        self.scoring_matrix_type = scoring_matrix_type
        self.llm = openai_client
        self.log_dir = log_dir

    def run(
        self, prompt_path: Path, base_name: str, iteration: int, workflow_id: str = None
    ):
        """
        Main entry point for evaluating a prompt.
        All events are logged to a central workflow JSONL file.
        """
        # Generate a workflow_id if not provided
        if workflow_id is None:
            workflow_id = f"{datetime.utcnow().isoformat(timespec='seconds').replace(':', '-')}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # --- Read prompt
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()

            # --- Call LLM
            llm_response = self.llm.chat_completion(prompt=prompt_content)
            first_message = (
                llm_response.choices[0].message["content"]
                if llm_response.choices and "content" in llm_response.choices[0].message
                else ""
            )

            # --- Prepare event payload
            payload = {
                "llm_output": first_message,
                "pass_threshold": False,  # You may want to evaluate against a real threshold here
                "feedback": "",
            }

            # --- Create and log success event
            event = AgentEvent(
                event_type="quality_check",
                agent_name="PromptQualityAgent",
                agent_version="1.3.1",
                timestamp=datetime.utcnow(),
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
            # --- On error, log error event with exception info
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="PromptQualityAgent",
                agent_version="1.3.1",
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
            raise  # Optionally: you can choose to only log and not re-raise
