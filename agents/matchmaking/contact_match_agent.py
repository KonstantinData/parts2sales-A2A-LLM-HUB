# agents/matchmaking/contact_match_agent.py

"""
Contact Match Agent

Version: 2.1.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Suggests potential contacts within matched companies based on provided company data.
Uses LLM for identifying plausible contact roles or names.
Logs all contact suggestions to workflow-centric JSONL log.
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


class ContactsMatched(BaseModel):
    """Schema for output of contact matching."""

    contacts: list  # Output as list of contact dicts or names


class ContactMatchAgent:
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
            workflow_id = f"contact_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            companies_json = json.dumps(input_data, ensure_ascii=False, indent=2)

            contacts_json = self.match_contacts(companies_json)
            validated = ContactsMatched(contacts=contacts_json)

            payload = {
                "input": input_data,
                "contacts": validated.contacts,
                "feedback": "",
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="contact_match",
                agent_name="ContactMatchAgent",
                agent_version="2.1.0",
                timestamp=cet_now(),
                step_id="contact_match",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "matching_strategy": "LLM",
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
                agent_name="ContactMatchAgent",
                agent_version="2.1.0",
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
                    "matching_strategy": "LLM",
                },
                workflow_id=workflow_id,
                source_event_id=parent_event_id,
            )
            logger.log_event(error_event)
            raise

    def match_contacts(self, companies_json: str):
        prompt = (
            "Given the following JSON array of company names, suggest 1-2 plausible B2B contact roles per company as a JSON array of objects "
            "with 'company' and 'contact_role' fields. Only output the JSON array, no explanations.\n\n"
            f"{companies_json}\n"
        )
        response = self.llm.chat(prompt=prompt)
        print("🧠 LLM Response (Contact):\n", response)
        return json.loads(response)
