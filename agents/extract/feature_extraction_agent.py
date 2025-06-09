# agents/extract/feature_extraction_agent.py

"""
Feature Extraction Agent

Version: 2.1.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Extracts features from provided input data using LLM.
Logging: All extraction events (success and error) are appended to a workflow-centric JSONL log using JsonlEventLogger.
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

    features: list  # Accept any list structure for generalization


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
        input_data: list,
        base_name: str,
        iteration: int,
        workflow_id: str = None,
        parent_event_id: str = None,
    ):
        if workflow_id is None:
            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # --- Prepare JSON string for LLM prompt
            input_content = json.dumps(input_data, ensure_ascii=False, indent=2)

            # --- LLM-based extraction
            features_json = self.extract_features(input_content)
            validated = FeaturesExtracted(features=features_json)

            payload = {
                "input": input_data,
                "features_extracted": validated.features,
                "feedback": "",
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="feature_extraction",
                agent_name="FeatureExtractionAgent",
                agent_version="2.1.0",
                timestamp=cet_now(),
                step_id="feature_extraction",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "extraction_strategy": "LLM",
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
                agent_name="FeatureExtractionAgent",
                agent_version="2.1.0",
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
                workflow_id=workflow_id,
                source_event_id=parent_event_id,
            )
            logger.log_event(error_event)
            raise

    def extract_features(self, input_content: str):
        prompt = (
            "Extract the most relevant product or business features from the following input JSON list.\n\n"
            f"{input_content}\n\n"
            "Return a JSON array of feature objects only (do not include any explanations)."
        )
        response = self.llm.chat(prompt=prompt)
        print("🧠 LLM Response:\n", response)
        # Try to parse as JSON list, or raise error
        return json.loads(response)
