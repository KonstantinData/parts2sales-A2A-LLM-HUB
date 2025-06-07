"""
crm_sync_agent.py

Purpose : Synchronizes data with CRM systems based on input and agent logic.
Logging : All events (success and error) are appended to a workflow-centric JSONL log via JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Every CRM sync run (success/error) is logged as an AgentEvent in the workflow log.
# - No scattered or legacy output files, only clean JSONL logs per workflow/session.
# - Designed for scalable, compliant, and auditable production integration.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from utils.time_utils import cet_now, timestamp_for_filename

from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger


class CRMSyncAgent:
    def __init__(self, sync_strategy, crm_client, log_dir=Path("logs/workflows")):
        """
        sync_strategy: logic/type for CRM sync (e.g., 'push', 'merge', 'update')
        crm_client: injected CRM API client or handler
        log_dir: workflow log storage (default: logs/workflows)
        """
        self.sync_strategy = sync_strategy
        self.crm_client = crm_client
        self.log_dir = log_dir

    def run(self, input_data, base_name: str, iteration: int, workflow_id: str = None):
        """
        Performs CRM sync operation on the given input.
        All events are logged to the workflow JSONL log.
        """
        if workflow_id is None:
            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # --- Sync with CRM (replace with your actual logic)
            sync_result = self.sync_with_crm(input_data)

            payload = {
                "input_data": input_data,
                "sync_result": sync_result,
                "feedback": "",
            }

            event = AgentEvent(
                event_type="crm_sync",
                agent_name="CRMSyncAgent",
                agent_version="1.0.0",
                timestamp=cet_now(),
                step_id="crm_sync",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "sync_strategy": str(self.sync_strategy),
                },
            )
            logger.log_event(event)
            return event

        except Exception as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="CRMSyncAgent",
                agent_version="1.0.0",
                timestamp=cet_now(),
                step_id="crm_sync",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                    "sync_strategy": str(self.sync_strategy),
                },
            )
            logger.log_event(error_event)
            raise

    def sync_with_crm(self, input_data):
        """
        Your CRM sync logic goes here.
        For now, returns a dummy result. Replace with your real CRM sync logic!
        """
        # Example: self.crm_client.push_data(input_data)
        return {"status": "success"}  # Placeholder
