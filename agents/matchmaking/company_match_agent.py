# agents/matchmaking/company_match_agent.py

"""
Company Match Agent

Version: 2.3.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Matches extracted industries or usecases to best-fit companies from a reference set or via LLM.
Logs all matchmaking events to workflow-centric JSONL log.
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


class CompaniesMatched(BaseModel):
    companies: list

    @classmethod
    def from_llm_response(cls, response):
        result = extract_list_anywhere(response, ["companies", "company_list"])
        if result and isinstance(result, list):
            return cls(companies=result)
        raise ValueError(
            "LLM response must contain a companies list under a common key or as root list."
        )


def flatten_for_llm(input_data):
    if isinstance(input_data, dict):
        for key in ["industries", "industry_classes", "sectors"]:
            if key in input_data and isinstance(input_data[key], list):
                return input_data[key]
    return input_data


class CompanyMatchAgent:
    def __init__(
        self,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
        prompt_dir=Path("prompts/01-template"),
        prompt_file="company_assign_template_v0.2.0.yaml",
    ):
        self.llm = openai_client
        self.log_dir = log_dir
        self.prompt_dir = prompt_dir
        self.prompt_file = prompt_file
        self.workflow_id = None

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

            workflow_id = f"company_{uuid4().hex[:6]}"
        self.workflow_id = workflow_id
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            industries_json = json.dumps(
                flatten_for_llm(input_data), ensure_ascii=False, indent=2
            )
            companies_json = self.match_companies(industries_json, prompt_override)
            validated = CompaniesMatched.from_llm_response(companies_json)

            payload = {
                "input": input_data,
                "companies": validated.companies,
                "feedback": "",
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="company_match",
                agent_name="CompanyMatchAgent",
                agent_version="2.3.0",
                timestamp=cet_now(),
                step_id="company_match",
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
                agent_name="CompanyMatchAgent",
                agent_version="2.3.0",
                timestamp=cet_now(),
                step_id="company_match",
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

    def match_companies(self, industries_json: str, prompt_override: str | None = None):
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
            f"Here is the industry input JSON list:\n{industries_json}\n"
            "Respond only as specified above."
        )
        if prompt_override:
            prompt = prompt_override

        response = self.llm.chat(prompt=prompt)
        print("🧠 Raw LLM Response (Company):")
        print(response)

        return json.loads(response)
