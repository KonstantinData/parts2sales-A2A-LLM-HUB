"""
industry_class_agent.py

Purpose : Classifies industry sectors from input using LLM or custom logic.
Logging : All events (success and error) are appended to a workflow-centric JSONL log via JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Every industry classification run (success/error) is logged as an AgentEvent in the workflow log.
# - No legacy output or scattered files, only workflow/session-based JSONL logs.
# - Ensures full traceability, compliance, and scalability.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient


class IndustryClassAgent:
    def __init__(
        self,
        classification_strategy,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        """
        classification_strategy: logic or type for industry classification (e.g., 'LLM', 'rules', etc.)
        openai_client: injected OpenAIClient instance
        log_dir: workflow log storage (default: logs/workflows)
        """
        self.classification_strategy = classification_strategy
        self.llm = openai_client
        self.log_dir = log_dir

    def run(
        self, input_path: Path, base_name: str, iteration: int, workflow_id: str = None
    ):
        """
        Performs industry classification on the given input.
        All events are logged to the workflow JSONL log.
        """
        if workflow_id is None:
            workflow_id = f"{datetime.utcnow().isoformat(timespec='seconds').replace(':', '-')}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # --- Read input data
            with open(input_path, "r", encoding="utf-8") as f:
                input_content = f.read()

            # --- Classify industries (customize this logic as needed)
            industry_classes = self.classify_industries(input_content)

            payload = {
                "input": input_content,
                "industry_classes": industry_classes,
                "feedback": "",
            }

            event = AgentEvent(
                event_type="industry_classification",
                agent_name="IndustryClassAgent",
                agent_version="1.0.0",
                timestamp=datetime.utcnow(),
                step_id="industry_classification",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "classification_strategy": str(self.classification_strategy),
                },
            )
            logger.log_event(event)
            return event

        except Exception as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="IndustryClassAgent",
                agent_version="1.0.0",
                timestamp=datetime.utcnow(),
                step_id="industry_classification",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                    "classification_strategy": str(self.classification_strategy),
                },
            )
            logger.log_event(error_event)
            raise

    def classify_industries(self, input_content):
        """
        Custom industry classification logic.
        For now, returns a dummy example. Replace with your real classification!
        """
        # Example: use LLM, keyword mapping, etc.
        # classes = self.llm.classify_industries(input_content)
        # return classes
        return ["example_industry"]  # Placeholder
