# agents/matchmaking/contact_match_agent.py

"""
Contact Match Agent

Version: 2.3.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Suggests potential contacts within matched companies based on provided company data.
Uses LLM for identifying plausible contact roles or names.
Logs all contact suggestions to workflow-centric JSONL log.
"""

from pathlib import Path
from uuid import uuid4
import json
import yaml

from pydantic import BaseModel, ValidationError
from utils.time_utils import cet_now
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient
from utils.list_extractor import extract_list_anywhere


class ContactsMatched(BaseModel):
    contacts: list

    @classmethod
    def from_llm_response(cls, response):
        result = extract_list_anywhere(response, ["contacts", "contact_list"])
        if result and isinstance(result, list):
            return cls(contacts=result)
        raise ValueError(
            "LLM response must contain a contacts list under a common key or as root list."
        )


class ContactMatchAgent:
    def __init__(
        self,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
        prompt_dir=Path("prompts/01-template"),
        prompt_file="contact_assign_template_v0.2.0.yaml",
    ):
        self.llm = openai_client
        self.log_dir = log_dir
        self.prompt_dir = prompt_dir
        self.prompt_file = prompt_file

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
            from utils.time_utils import timestamp_for_filename

            workflow_id = f"contact_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            companies_json = json.dumps(input_data, ensure_ascii=False, indent=2)
            contacts_json = self.match_contacts(companies_json, prompt_override)
            validated = ContactsMatched.from_llm_response(contacts_json)

            payload = {
                "input": input_data,
                "contacts": validated.contacts,
                "feedback": "",
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="contact_match",
                agent_name="ContactMatchAgent",
                agent_version="2.3.0",
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
                agent_version="2.3.0",
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

    def match_contacts(self, companies_json: str, prompt_override: str | None = None):
        prompt_path = self.prompt_dir / self.prompt_file
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_yaml = yaml.safe_load(f)
        system_prompt = (
            f"{prompt_yaml['role'].strip()}\n\n"
            f"{prompt_yaml['objective'].strip()}\n"
            f"INPUT FORMAT:\n{prompt_yaml['input_format'].strip()}\n"
            f"OUTPUT FORMAT:\n{prompt_yaml['output_format'].strip()}\n"
            f"CONSTRAINTS:\n" + "\n".join(f"- {c}" for c in prompt_yaml["constraints"])
        )
        prompt = (
            f"{system_prompt}\n\n"
            f"Here is the company input JSON list:\n{companies_json}\n"
            "Respond only as specified above."
        )
        if prompt_override:
            prompt = prompt_override
        response = self.llm.chat(prompt=prompt)
        print("🧠 LLM Response (Contact):\n", response)
        return json.loads(response)
