"""
CRM Sync Agent

Version: 2.2.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Simulates syncing of matched contacts into a CRM system (real or mock). Logs all sync events to the workflow-centric JSONL log. Accepts pipeline input and makes output history/trace clear.
"""

from pathlib import Path
from uuid import uuid4
import json

from pydantic import BaseModel, ValidationError
from utils.time_utils import cet_now
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient


class CRMSyncResult(BaseModel):
    synced_contacts: list
    sync_status: str

    @classmethod
    def from_llm_response(cls, response):
        if (
            isinstance(response, dict)
            and "synced_contacts" in response
            and "sync_status" in response
        ):
            return cls(**response)
        raise ValueError(
            "LLM response must be a dict with 'synced_contacts' and 'sync_status'."
        )


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
        prompt_override: str | None = None,
    ):
        if workflow_id is None:
            workflow_id = f"crm_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            contacts_json = json.dumps(input_data, ensure_ascii=False, indent=2)
            result = self.sync_contacts(contacts_json, prompt_override)
            validated = CRMSyncResult.from_llm_response(result)

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
                agent_version="2.2.0",
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
                agent_version="2.2.0",
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

    def sync_contacts(self, contacts_json: str, prompt_override: str | None = None):
        # In real use, integrate CRM API here. For now: simulate.
        if prompt_override:
            try:
                response = self.llm.chat(prompt=prompt_override)
                return json.loads(response)
            except Exception:
                return {
                    "synced_contacts": [],
                    "sync_status": "failed",
                }
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
