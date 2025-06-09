# agents/matchmaking/crm_sync_agent.py

"""
CRM Sync Agent

Version: 2.1.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Simulates syncing of matched contacts into a CRM system.
Logs all sync events to the workflow-centric JSONL log.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4
import json

from pydantic import BaseModel, ValidationError
from utils.time_utils import cet_now
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient


class CRMSyncResult(BaseModel):
    """Schema for CRM sync operation result."""

    synced_contacts: list
    sync_status: str


class CRMSyncAgent:
    def __init__(
        self,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        self.llm = openai_client
        self.log_dir = log_dir

    def run(
        self,
        input_data: list,
        base_name: str,
        iteration: int,
        workflow_id: str = None,
        parent_event_id: str = None,
    ):
        if workflow_id is None:
            workflow_id = f"crm_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            contacts_json = json.dumps(input_data, ensure_ascii=False, indent=2)

            result = self.sync_contacts(contacts_json)
            validated = CRMSyncResult(**result)

            payload = {
                "input": input_data,
                "synced_contacts": validated.synced_contacts,
                "sync_status": validated.sync_status,
                "feedback": "",
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="crm_sync",
                agent_name="CRMSyncAgent",
                agent_version="2.1.0",
                timestamp=cet_now(),
                step_id="crm_sync",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "sync_strategy": "simulated",
                },
                workflow_id=workflow_id,
                source_event_id=parent_event_id,
            )
            logger.log_event(event)
            return event

        except (ValidationError, Exception) as ex:
            import traceback

            error_event = AgentEvent(
                event_id=str(uuid4()),
                event_type="error",
                agent_name="CRMSyncAgent",
                agent_version="2.1.0",
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
                    "sync_strategy": "simulated",
                },
                workflow_id=workflow_id,
                source_event_id=parent_event_id,
            )
            logger.log_event(error_event)
            raise

    def sync_contacts(self, contacts_json: str):
        # Simulate CRM sync – in real use, integrate CRM API here.
        try:
            contacts = json.loads(contacts_json)
            return {
                "synced_contacts": contacts,
                "sync_status": "success",
            }
        except Exception:
            return {
                "synced_contacts": [],
                "sync_status": "failed",
            }
