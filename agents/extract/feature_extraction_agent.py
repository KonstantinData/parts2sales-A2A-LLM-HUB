# agents/extract/feature_extraction_agent.py

"""
Feature Extraction Agent

Version: 2.3.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Extracts features from provided input data using LLM.
Loads the extraction prompt from the correct YAML template layer and injects all
specification and constraints to guide the LLM toward structured, specification-grade extraction.
All extraction events (success and error) are appended to a workflow-centric JSONL log using JsonlEventLogger.
"""

from pathlib import Path
from uuid import uuid4
import json
import yaml

from pydantic import BaseModel, ValidationError
from utils.time_utils import cet_now, timestamp_for_filename
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient
from utils.list_extractor import extract_list_anywhere


class FeaturesExtracted(BaseModel):
    features: list

    @classmethod
    def from_llm_response(cls, response):
        result = extract_list_anywhere(response, ["features", "features_extracted"])
        if result and isinstance(result, list):
            return cls(features=result)
        raise ValueError(
            "LLM response must contain a features list under a common key or as root list."
        )


class FeatureExtractionAgent:
    def __init__(
        self,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
        prompt_dir=Path("prompts/01-template"),
        prompt_file="feature_setup_template_v0.2.0.yaml",
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
            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            input_content = json.dumps(input_data, ensure_ascii=False, indent=2)
            features_json = self.extract_features(input_content, prompt_override)
            validated = FeaturesExtracted.from_llm_response(features_json)

            payload = {
                "input": input_data,
                "features_extracted": validated.features,
                "feedback": "",
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="feature_extraction",
                agent_name="FeatureExtractionAgent",
                agent_version="2.3.0",
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
                agent_version="2.3.0",
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

    def extract_features(self, input_content: str, prompt_override: str | None = None):
        prompt_path = self.prompt_dir / self.prompt_file
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_yaml = yaml.safe_load(f)

        system_prompt = (
            f"{prompt_yaml['role'].strip()}\n\n"
            f"{prompt_yaml['objective'].strip()}\n"
            f"INPUT FORMAT (each product):\n{prompt_yaml['input_format'].strip()}\n"
            f"OUTPUT FORMAT:\n{prompt_yaml['output_format'].strip()}\n"
            f"CONSTRAINTS:\n" + "\n".join(f"- {c}" for c in prompt_yaml["constraints"])
        )

        prompt = (
            f"{system_prompt}\n\n"
            f"Here is the product input JSON list:\n{input_content}\n"
            "Respond only as specified above."
        )

        if prompt_override:
            prompt = prompt_override

        response = self.llm.chat(prompt=prompt)
        print("🧠 LLM Response:\n", response)
        return json.loads(response)
