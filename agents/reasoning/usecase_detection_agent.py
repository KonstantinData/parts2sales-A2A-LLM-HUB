# agents/reasoning/usecase_detection_agent.py

"""
Usecase Detection Agent

Version: 2.1.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Infers plausible usage domains for products based on structured features.
Uses LLM for semantic mapping of features to use cases.
Logs all detections to the workflow-centric JSONL log.
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


class UsecasesExtracted(BaseModel):
    """Schema for output of usecase detection."""

    usecases: list  # Generalized output for usecases


class UsecaseDetectionAgent:
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
            workflow_id = f"usecase_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # Prepare JSON string for LLM
            features_json = json.dumps(input_data, ensure_ascii=False, indent=2)

            usecases_json = self.extract_usecases(features_json, prompt_override)
            validated = UsecasesExtracted(usecases=usecases_json)

            payload = {
                "input": input_data,
                "usecases": validated.usecases,
                "feedback": "",
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="usecase_detection",
                agent_name="UsecaseDetectionAgent",
                agent_version="2.1.0",
                timestamp=cet_now(),
                step_id="usecase_detection",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "mapping_strategy": "LLM",
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
                agent_name="UsecaseDetectionAgent",
                agent_version="2.1.0",
                timestamp=cet_now(),
                step_id="usecase_detection",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                    "mapping_strategy": "LLM",
                },
                workflow_id=workflow_id,
                source_event_id=parent_event_id,
            )
            logger.log_event(error_event)
            raise

    def extract_usecases(self, features_json: str, prompt_override: str | None = None):
        prompt = (
            "Given the following extracted product features as JSON, "
            "infer and return 3 to 7 plausible usage domains (application environments, use cases) as a JSON array of strings. "
            "Do not include explanations, only the JSON list.\n\n"
            f"{features_json}\n"
        )
        if prompt_override:
            prompt = prompt_override
        response = self.llm.chat(prompt=prompt)
        print("🧠 LLM Response (Usecase):\n", response)
        return json.loads(response)
