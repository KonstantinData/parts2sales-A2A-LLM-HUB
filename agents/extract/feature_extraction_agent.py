"""
feature_extraction_agent.py

Purpose : Extracts features from prompts or input data using LLM.
Logging : All extraction events (success and error) are appended to a workflow-centric JSONL log using JsonlEventLogger.

Version : 2.0.0
Author  : Konstantin Milonas with support from AI Copilot
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4
import json

from pydantic import BaseModel, ValidationError
from utils.time_utils import cet_now, timestamp_for_filename
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient


class FeaturesExtracted(BaseModel):
    """Output schema for features extracted by the agent."""

    example_feature: bool


class FeatureExtractionAgent:
    def __init__(
        self,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        self.llm = openai_client
        self.log_dir = log_dir

    def run(
        self,
        input_path: Path,
        base_name: str,
        iteration: int,
        workflow_id: str = None,
        parent_event_id: str = None,
    ):
        if workflow_id is None:
            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                input_content = f.read()

            features_json = self.extract_features(input_content)

            validated = FeaturesExtracted(**features_json)

            payload = {
                "input": input_content,
                "features_extracted": validated.dict(),
                "feedback": "",
            }

            event = AgentEvent(
                event_type="feature_extraction",
                agent_name="FeatureExtractionAgent",
                agent_version="2.0.0",
                timestamp=cet_now(),
                step_id="feature_extraction",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "extraction_strategy": "LLM",
                },
                source_event_id=parent_event_id,
            )
            logger.log_event(event)
            return event

        except (ValidationError, Exception) as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="FeatureExtractionAgent",
                agent_version="2.0.0",
                timestamp=cet_now(),
                step_id="feature_extraction",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                    "extraction_strategy": "LLM",
                },
                source_event_id=parent_event_id,
            )
            logger.log_event(error_event)
            raise

    def extract_features(self, input_content):
        prompt = (
            f"Extract relevant product or business features from the following input:\n\n"
            f"{input_content}\n\nReturn a JSON object."
        )
        response = self.llm.chat(prompt=prompt)
        return json.loads(response)
