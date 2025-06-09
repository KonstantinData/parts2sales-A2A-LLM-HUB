# agents/matchmaking/company_match_agent.py

"""
Company Match Agent

Version: 2.1.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Matches extracted industries or usecases to best-fit companies from a reference set or via LLM.
Logs all matchmaking events to workflow-centric JSONL log.
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


class CompaniesMatched(BaseModel):
    """Schema for company match output."""

    companies: list  # General output structure (company names or dicts)


class CompanyMatchAgent:
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
            workflow_id = f"company_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            industries_json = json.dumps(input_data, ensure_ascii=False, indent=2)

            companies_json = self.match_companies(industries_json)
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
                agent_version="2.1.0",
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
                agent_version="2.1.0",
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

    def match_companies(self, industries_json: str):
        prompt = (
            "Given the following JSON array of industry classes, suggest 3 to 7 example companies (real or plausible for the market) "
            "as a JSON array of company names. Return only the JSON array, no explanations.\n\n"
            f"{industries_json}\n"
        )
        response = self.llm.chat(prompt=prompt)
        print("🧠 LLM Response (Company):\n", response)
        return json.loads(response)
