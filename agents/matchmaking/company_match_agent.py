"""
Company Match Agent

Version: 2.1.4
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Matches extracted industries or usecases to best-fit companies from a reference set or via LLM.
Logs all matchmaking events to workflow-centric JSONL log.
"""

from pathlib import Path
from uuid import uuid4
import json
import traceback

from pydantic import BaseModel, ValidationError
from utils.time_utils import cet_now
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient
from utils.json_safety import extract_json_array_from_response


class CompaniesMatched(BaseModel):
    """Schema for company match output."""

    companies: list  # General output structure (company names or dicts)


def flatten_for_llm(input_data):
    """Falls input_data ein dict mit 'industries' o.ä. ist, nimm nur das relevante Array."""
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
    ):
        self.llm = openai_client
        self.log_dir = log_dir
        self.workflow_id = None  # Wird dynamisch gesetzt in run()

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
            workflow_id = f"company_{uuid4().hex[:6]}"
        self.workflow_id = workflow_id
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            industries_json = json.dumps(
                flatten_for_llm(input_data), ensure_ascii=False, indent=2
            )
            companies_json = self.match_companies(industries_json, prompt_override)
            validated = CompaniesMatched(companies=companies_json)

            payload = {
                "input": input_data,
                "companies": validated.companies,
                "feedback": "",
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="company_match",
                agent_name="CompanyMatchAgent",
                agent_version="2.1.4",
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
            error_event = AgentEvent(
                event_id=str(uuid4()),
                event_type="error",
                agent_name="CompanyMatchAgent",
                agent_version="2.1.4",
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
        prompt = (
            "Given the following JSON array of industry classes, suggest 3 to 7 example companies "
            "(real or plausible for the market) as a JSON array of company names. "
            "Return only the JSON array, no explanations.\n\n"
            f"{industries_json}\n"
        )
        if prompt_override:
            prompt = prompt_override

        print("📤 Prompt sent to LLM:")
        print(prompt)

        response = ""  # Sicherstellen, dass response immer definiert ist

        try:
            response = self.llm.chat(prompt=prompt)
            print("🧠 Raw LLM Response (Company):")
            print(response)

            # Frühzeitig Klartext abfangen
            first = response.lstrip()
            if not first.startswith("[") and not first.startswith("{"):
                raise ValueError(
                    f"LLM response is not JSON but natural language: {first[:80]}"
                )

            result = extract_json_array_from_response(response)

            if not isinstance(result, list):
                raise ValueError(f"Expected a list, got: {type(result)} → {result}")
            if not all(isinstance(item, str) for item in result):
                raise ValueError(
                    "Expected list of strings (company names). Got: " + str(result)
                )

            return result

        except Exception as ex:
            logger = JsonlEventLogger(
                workflow_id=self.workflow_id, log_dir=self.log_dir
            )
            error_details = {
                "exception": str(ex),
                "traceback": traceback.format_exc(),
                "prompt": prompt,
                "response": response or "<no response>",
            }
            logger.log_event(
                {
                    "event_id": str(uuid4()),
                    "event_type": "error",
                    "agent_name": "CompanyMatchAgent",
                    "agent_version": "2.1.4",
                    "timestamp": cet_now(),
                    "step_id": "match_companies",
                    "prompt_version": "enhanced_validation",
                    "status": "error",
                    "payload": error_details,
                    "meta": {
                        "context": "JSON parsing and validation",
                    },
                    "workflow_id": self.workflow_id,
                    "source_event_id": None,
                }
            )
            raise
