# controller/agent_orchestrator.py

"""
Agent Orchestrator for 01-template pipeline processing with sequential agent calls,
versioning, feedback loops, and staged environment promotion.
"""
import sys
from pathlib import Path

import json
from utils.openai_client import OpenAIClient
from agents.extract.feature_extraction_agent import FeatureExtractionAgent
from agents.reasoning.usecase_detection_agent import UsecaseDetectionAgent
from agents.reasoning.industry_class_agent import IndustryClassAgent
from agents.matchmaking.company_match_agent import CompanyMatchAgent
from agents.prompt_quality_agent import PromptQualityAgent
from agents.prompt_improvement_agent import PromptImprovementAgent
from utils.jsonl_event_logger import JsonlEventLogger
import yaml


class AgentOrchestrator:
    def __init__(self, workflow_id: str, sample_file: Path, log_dir: Path):
        self.workflow_id = workflow_id
        self.sample_file = sample_file
        self.log_dir = log_dir
        self.openai_client = OpenAIClient()

        with open("config/max_retries.yaml", "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        self.max_retries = cfg.get("max_retries", 1)

        self.feature_agent = FeatureExtractionAgent(
            openai_client=self.openai_client,
            log_dir=self.log_dir,
        )
        self.usecase_agent = UsecaseDetectionAgent(
            openai_client=self.openai_client,
            log_dir=self.log_dir,
        )
        self.industry_agent = IndustryClassAgent(
            openai_client=self.openai_client,
            log_dir=self.log_dir,
        )
        self.company_agent = CompanyMatchAgent(
            openai_client=self.openai_client,
            log_dir=self.log_dir,
        )
        self.quality_agent = PromptQualityAgent(
            openai_client=self.openai_client,
            log_dir=self.log_dir,
        )
        self.improvement_agent = PromptImprovementAgent(
            openai_client=self.openai_client,
            log_dir=self.log_dir,
        )

    def _run_with_quality(
        self,
        agent,
        input_data,
        base_name: str,
        iteration: int,
        parent_event_id: str | None = None,
    ):
        current_event = agent.run(
            input_data=input_data,
            base_name=base_name,
            iteration=iteration,
            workflow_id=self.workflow_id,
            parent_event_id=parent_event_id,
        )

        retries = 0
        while retries < self.max_retries:
            quality_event = self.quality_agent.run(
                input_data=current_event.payload,
                base_name=base_name,
                iteration=iteration,
                workflow_id=self.workflow_id,
                parent_event_id=current_event.event_id,
            )

            passed = quality_event.payload["evaluation"]["passed"]
            if passed:
                break

            improvement_event = self.improvement_agent.run(
                {
                    "original_prompt": base_name,
                    "output": current_event.payload,
                    "feedback": quality_event.payload["evaluation"],
                },
                base_name=base_name,
                iteration=iteration,
                workflow_id=self.workflow_id,
                parent_event_id=quality_event.event_id,
            )

            improved_prompt = improvement_event.payload["improved_prompt"]
            retries += 1

            current_event = agent.run(
                input_data=input_data,
                base_name=base_name,
                iteration=iteration,
                workflow_id=self.workflow_id,
                parent_event_id=improvement_event.event_id,
                prompt_override=improved_prompt,
            )

        return current_event

    def run(self, base_name: str, iteration: int):
        # Load sample data once and pass as input data to agents
        with open(self.sample_file, "r", encoding="utf-8") as f:
            sample_data = json.load(f)

        # Step 1: Feature Extraction
        feature_event = self._run_with_quality(
            self.feature_agent,
            input_data=sample_data,
            base_name=base_name.replace(
                "usecase_detect_template",
                "feature_setup_template",
            ),
            iteration=iteration,
        )
        feature_payload = feature_event.payload

        # Step 2: Usecase Detection
        usecase_event = self._run_with_quality(
            self.usecase_agent,
            input_data=feature_payload,
            base_name=base_name.replace(
                "feature_setup_template",
                "usecase_detect_template",
            ),
            iteration=iteration,
            parent_event_id=feature_event.event_id,
        )
        usecase_payload = usecase_event.payload

        # Step 3: Industry Classification
        industry_event = self._run_with_quality(
            self.industry_agent,
            input_data=usecase_payload,
            base_name=base_name.replace(
                "usecase_detect_template",
                "industry_class_template",
            ),
            iteration=iteration,
            parent_event_id=usecase_event.event_id,
        )
        industry_payload = industry_event.payload

        # Step 4: Company Assignment
        company_event = self._run_with_quality(
            self.company_agent,
            input_data=industry_payload,
            base_name=base_name.replace(
                "industry_class_template",
                "company_assign_template",
            ),
            iteration=iteration,
            parent_event_id=industry_event.event_id,
        )

        # Final output is company_event.payload; further processing can be added here.

        return company_event
