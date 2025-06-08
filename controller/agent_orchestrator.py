# controller/agent_orchestrator.py

"""
agent_orchestrator.py

Purpose : Orchestrates agent-to-agent processing with retry and validation.
Version : 2.0.0
Author  : Konstantin Milonas with Agentic AI Copilot support
"""

from pathlib import Path
from uuid import uuid4

from utils.time_utils import timestamp_for_filename
from utils.openai_client import OpenAIClient
from utils.agent_outputs import FeatureExtractionOutput
from agents.extract.feature_extraction_agent import FeatureExtractionAgent
from agents.prompt_quality_agent import PromptQualityAgent


class AgentOrchestrator:
    def __init__(self):
        self.workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        self.log_dir = Path("logs/workflows")
        self.openai_client = OpenAIClient()
        self.extractor = FeatureExtractionAgent(
            openai_client=self.openai_client, log_dir=self.log_dir
        )
        self.scorer = PromptQualityAgent(
            openai_client=self.openai_client, log_dir=self.log_dir
        )

    def run(self, input_path: Path, base_name: str, iteration: int):
        # Feature Extraction
        extraction_event = self.extractor.run(
            input_path=input_path,
            base_name=base_name,
            iteration=iteration,
            workflow_id=self.workflow_id,
        )

        if extraction_event.status != "success":
            if extraction_event.meta.get("retry_allowed", False):
                retry_count = extraction_event.meta.get("retry_count", 0) + 1
                retry_event = self.extractor.run(
                    input_path=input_path,
                    base_name=base_name,
                    iteration=iteration,
                    workflow_id=self.workflow_id,
                )
                extraction_event = retry_event

            if extraction_event.status != "success":
                print("❌ Feature extraction failed. Aborting pipeline.")
                return

        # FeatureExtractionOutput Schema Validation
        try:
            feature_output = FeatureExtractionOutput.model_validate(
                extraction_event.payload
            )
        except Exception as ex:
            print(f"❌ Schema validation failed: {ex}")
            return

        # Prompt Quality Scoring
        quality_event = self.scorer.run(
            input_data=feature_output,
            base_name=base_name,
            iteration=iteration,
            workflow_id=self.workflow_id,
            parent_event_id=extraction_event.event_id,
        )

        if quality_event.status != "success":
            print("⚠️ Prompt quality scoring failed.")
        else:
            print("✅ Prompt quality scoring succeeded.")
