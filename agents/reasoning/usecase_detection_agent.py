"""
usecase_detection_agent.py

Purpose : Detects relevant use cases from input using LLM or predefined logic.
Logging : All events (success and error) are appended to a workflow-centric JSONL log via JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Every use case detection run (success/error) is logged as an AgentEvent in the workflow log.
# - No scattered output files, only clean JSONL logging per workflow/session.
# - Ensures full traceability and easy scaling/monitoring.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient


class UsecaseDetectionAgent:
    def __init__(
        self,
        detection_strategy,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        """
        detection_strategy: logic or type for use case detection (could be 'LLM', 'rules', etc.)
        openai_client: injected OpenAIClient instance
        log_dir: workflow log storage (default: logs/workflows)
        """
        self.detection_strategy = detection_strategy
        self.llm = openai_client
        self.log_dir = log_dir

    def run(
        self, input_path: Path, base_name: str, iteration: int, workflow_id: str = None
    ):
        """
        Performs use case detection on the given input.
        All events are logged to the workflow JSONL log.
        """
        if workflow_id is None:
            workflow_id = f"{datetime.utcnow().isoformat(timespec='seconds').replace(':', '-')}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # --- Read input data
            with open(input_path, "r", encoding="utf-8") as f:
                input_content = f.read()

            # --- Detect use cases (customize this logic as needed)
            detected_usecases = self.detect_usecases(input_content)

            payload = {
                "input": input_content,
                "detected_usecases": detected_usecases,
                "feedback": "",
            }

            event = AgentEvent(
                event_type="usecase_detection",
                agent_name="UsecaseDetectionAgent",
                agent_version="1.0.0",
                timestamp=datetime.utcnow(),
                step_id="usecase_detection",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "detection_strategy": str(self.detection_strategy),
                },
            )
            logger.log_event(event)
            return event

        except Exception as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="UsecaseDetectionAgent",
                agent_version="1.0.0",
                timestamp=datetime.utcnow(),
                step_id="usecase_detection",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                    "detection_strategy": str(self.detection_strategy),
                },
            )
            logger.log_event(error_event)
            raise

    def detect_usecases(self, input_content):
        """
        Your custom use case detection logic.
        For now, returns a dummy example. Replace with your real detection strategy!
        """
        # Example: use LLM, rules, keyword search, etc.
        # usecases = self.llm.detect_usecases(input_content)
        # return usecases
        return ["example_usecase"]  # Placeholder
