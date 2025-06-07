"""
feature_extraction_agent.py

Purpose : Extracts features from prompts or input data using LLM or custom rules.
Logging : All extraction events (success and error) are appended to a workflow-centric JSONL log using JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Every feature extraction run (success/error) is an AgentEvent in the workflow log.
# - No distributed output files, only clean JSONL logging per workflow/session.
# - Enables full traceability, monitoring, and future scaling.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from utils.time_utils import cet_now, timestamp_for_filename

from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient


class FeatureExtractionAgent:
    def __init__(
        self,
        extraction_strategy,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        """
        extraction_strategy: logic or type for feature extraction (could be 'LLM', 'regex', etc.)
        openai_client: injected OpenAIClient instance
        log_dir: workflow log storage (default: logs/workflows)
        """
        self.extraction_strategy = extraction_strategy
        self.llm = openai_client
        self.log_dir = log_dir

    def run(
        self, input_path: Path, base_name: str, iteration: int, workflow_id: str = None
    ):
        """
        Performs feature extraction from the given input.
        All events are logged to the workflow JSONL log.
        """
        if workflow_id is None:
            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # --- Read input data
            with open(input_path, "r", encoding="utf-8") as f:
                input_content = f.read()

            # --- Extract features (customize this logic as needed)
            extracted_features = self.extract_features(input_content)

            payload = {
                "input": input_content,
                "features_extracted": extracted_features,
                "feedback": "",
            }

            event = AgentEvent(
                event_type="feature_extraction",
                agent_name="FeatureExtractionAgent",
                agent_version="1.0.0",
                timestamp=cet_now(),
                step_id="feature_extraction",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "extraction_strategy": str(self.extraction_strategy),
                },
            )
            logger.log_event(event)
            return event

        except Exception as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="FeatureExtractionAgent",
                agent_version="1.0.0",
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
                    "extraction_strategy": str(self.extraction_strategy),
                },
            )
            logger.log_event(error_event)
            raise

    def extract_features(self, input_content):
        """
        Custom feature extraction logic.
        For now, returns a dummy example. Replace with your own extraction strategy!
        """
        # Example: use LLM or regex, etc.
        # features = self.llm.extract_features(input_content)
        # return features
        return {"example_feature": True}  # Placeholder
