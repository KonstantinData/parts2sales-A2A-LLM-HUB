# agents/reasoning/industry_class_agent.py

"""
Industry Classification Agent

Version: 2.3.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Assigns relevant industry classes based on detected usecases.
Uses LLM for semantic classification.
Logs all events to workflow-centric JSONL log.
"""

from pathlib import Path
from uuid import uuid4
import json

from pydantic import BaseModel, ValidationError
from utils.time_utils import cet_now
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient
from utils.list_extractor import extract_list_anywhere


class IndustriesExtracted(BaseModel):
    industries: list

    @classmethod
    def from_llm_response(cls, response):
        result = extract_list_anywhere(
            response, ["industries", "industry_classes", "labels"]
        )
        if result and isinstance(result, list):
            return cls(industries=result)
        raise ValueError(
            "LLM response must contain an industries list under a common key or as root list."
        )


class IndustryClassAgent:
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
            workflow_id = f"industry_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            usecases_json = json.dumps(input_data, ensure_ascii=False, indent=2)
            industries_json = self.extract_industries(usecases_json, prompt_override)
            validated = IndustriesExtracted.from_llm_response(industries_json)

            payload = {
                "input": input_data,
                "industries": validated.industries,
                "feedback": "",
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="industry_classification",
                agent_name="IndustryClassAgent",
                agent_version="2.3.0",
                timestamp=cet_now(),
                step_id="industry_classification",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "classification_strategy": "LLM",
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
                agent_name="IndustryClassAgent",
                agent_version="2.3.0",
                timestamp=cet_now(),
                step_id="industry_classification",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                    "classification_strategy": "LLM",
                },
                workflow_id=workflow_id,
                source_event_id=parent_event_id,
            )
            logger.log_event(error_event)
            raise

    def extract_industries(
        self, usecases_json: str, prompt_override: str | None = None
    ):
        prompt = (
            "Given the following JSON array of use cases, assign and return relevant industry classes (e.g. NAICS, NACE, or text labels) as a JSON array or dict.\n"
            "Respond ONLY with the JSON array or a dict, no explanations or comments.\n\n"
            f"{usecases_json}\n"
        )
        if prompt_override:
            prompt = prompt_override
        response = self.llm.chat(prompt=prompt)
        print("🧠 LLM Response (Industry):\n", response)
        return json.loads(response)
