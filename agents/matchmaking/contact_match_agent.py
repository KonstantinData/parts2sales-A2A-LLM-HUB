"""
contact_match_agent.py

Purpose : Matches contacts based on input using LLM or custom logic.
Logging : All events (success and error) are appended to a workflow-centric JSONL log via JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Every contact matching run (success/error) is logged as an AgentEvent in the workflow log.
# - No scattered or legacy output files, only clean JSONL logs per workflow/session.
# - Enables scalable, auditable, and production-ready operation.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from utils.time_utils import cet_now, timestamp_for_filename

from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient


class ContactMatchAgent:
    def __init__(
        self,
        match_strategy,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        """
        match_strategy: logic or type for contact matching (e.g., 'LLM', 'rules', etc.)
        openai_client: injected OpenAIClient instance
        log_dir: workflow log storage (default: logs/workflows)
        """
        self.match_strategy = match_strategy
        self.llm = openai_client
        self.log_dir = log_dir

    def run(
        self, input_path: Path, base_name: str, iteration: int, workflow_id: str = None
    ):
        """
        Performs contact matching on the given input.
        All events are logged to the workflow JSONL log.
        """
        if workflow_id is None:
            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # --- Read input data
            with open(input_path, "r", encoding="utf-8") as f:
                input_content = f.read()

            # --- Match contacts (customize this logic as needed)
            matched_contacts = self.match_contacts(input_content)

            payload = {
                "input": input_content,
                "matched_contacts": matched_contacts,
                "feedback": "",
            }

            event = AgentEvent(
                event_type="contact_match",
                agent_name="ContactMatchAgent",
                agent_version="1.0.0",
                timestamp=cet_now(),
                step_id="contact_match",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "match_strategy": str(self.match_strategy),
                },
            )
            logger.log_event(event)
            return event

        except Exception as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="ContactMatchAgent",
                agent_version="1.0.0",
                timestamp=cet_now(),
                step_id="contact_match",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                    "match_strategy": str(self.match_strategy),
                },
            )
            logger.log_event(error_event)
            raise

    def match_contacts(self, input_content):
        """
        Your contact matching logic here.
        For now, returns a dummy example. Replace with your real matching logic!
        """
        # Example: use LLM, CRM, or rule-based matching
        # contacts = self.llm.match_contacts(input_content)
        # return contacts
        return ["example_contact"]  # Placeholder
