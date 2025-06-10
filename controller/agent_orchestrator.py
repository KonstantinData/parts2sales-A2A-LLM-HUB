# controller/agent_orchestrator.py

"""
Agent Orchestrator for 01-template pipeline processing with sequential agent calls,
versioning, feedback loops, and staged environment promotion.
Holistische Pipeline: Jeder PromptQualityAgent bekommt agent_history als Kontext.
"""

import sys
from pathlib import Path
import json
import yaml

from utils.openai_client import OpenAIClient
from agents.extract.feature_extraction_agent import FeatureExtractionAgent
from agents.reasoning.usecase_detection_agent import UsecaseDetectionAgent
from agents.reasoning.industry_class_agent import IndustryClassAgent
from agents.matchmaking.company_match_agent import CompanyMatchAgent
from agents.prompt_quality_agent import PromptQualityAgent
from agents.prompt_improvement_agent import PromptImprovementAgent
from utils.jsonl_event_logger import JsonlEventLogger


class AgentOrchestrator:
    def __init__(
        self,
        workflow_id: str,
        sample_file: Path,
        log_dir: Path,
        prompt_dir: Path = Path("prompts/01-template"),
    ):
        self.workflow_id = workflow_id
        self.sample_file = sample_file
        self.log_dir = log_dir
        self.prompt_dir = prompt_dir
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
        agent_history: list,
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

        agent_history.append(
            {
                "agent": agent.__class__.__name__,
                "event": current_event.payload,
                "event_id": current_event.event_id,
                "step_id": current_event.step_id,
            }
        )

        while retries < self.max_retries:
            quality_event = self.quality_agent.run(
                input_data=current_event.payload,
                agent_history=agent_history.copy(),
                base_name=base_name,
                iteration=iteration,
                workflow_id=self.workflow_id,
                parent_event_id=current_event.event_id,
            )

            passed = quality_event.payload["evaluation"]["passed"]
            improve_for = quality_event.payload["evaluation"].get(
                "suggest_improvement_for"
            )

            if passed and not improve_for:
                break

            if improve_for:
                idx = next(
                    (
                        i
                        for i, item in reversed(list(enumerate(agent_history)))
                        if item["agent"] == improve_for
                        or item["step_id"] == improve_for
                    ),
                    None,
                )
                if idx is None:
                    raise ValueError(
                        f"Cannot find agent/step for improvement: {improve_for}"
                    )

                improve_target = agent_history[idx]
                improvement_event = self.improvement_agent.run(
                    {
                        "original_prompt": base_name,
                        "output": improve_target["event"],
                        "feedback": quality_event.payload["evaluation"],
                    },
                    base_name=base_name,
                    iteration=iteration,
                    workflow_id=self.workflow_id,
                    parent_event_id=quality_event.event_id,
                )
                improved_prompt = improvement_event.payload["improved_prompt"]

                agent_to_rerun = {
                    "FeatureExtractionAgent": self.feature_agent,
                    "UsecaseDetectionAgent": self.usecase_agent,
                    "IndustryClassAgent": self.industry_agent,
                    "CompanyMatchAgent": self.company_agent,
                }[improve_for]

                new_event = agent_to_rerun.run(
                    input_data=(
                        input_data if idx == 0 else agent_history[idx - 1]["event"]
                    ),
                    base_name=base_name,
                    iteration=iteration,
                    workflow_id=self.workflow_id,
                    parent_event_id=improvement_event.event_id,
                    prompt_override=improved_prompt,
                )
                agent_history[idx] = {
                    "agent": agent_to_rerun.__class__.__name__,
                    "event": new_event.payload,
                    "event_id": new_event.event_id,
                    "step_id": new_event.step_id,
                }
                current_event = new_event
                retries += 1
                continue

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

            current_event = agent.run(
                input_data=input_data,
                base_name=base_name,
                iteration=iteration,
                workflow_id=self.workflow_id,
                parent_event_id=improvement_event.event_id,
                prompt_override=improved_prompt,
            )
            agent_history[-1] = {
                "agent": agent.__class__.__name__,
                "event": current_event.payload,
                "event_id": current_event.event_id,
                "step_id": current_event.step_id,
            }
            retries += 1

        return current_event

    def run(self, base_name: str, iteration: int):
        with open(self.sample_file, "r", encoding="utf-8") as f:
            sample_data = json.load(f)

        agent_history = []

        feature_event = self._run_with_quality(
            self.feature_agent,
            input_data=sample_data,
            base_name=base_name.replace(
                "usecase_detect_template", "feature_setup_template"
            ),
            iteration=iteration,
            agent_history=agent_history,
        )
        feature_payload = feature_event.payload

        usecase_event = self._run_with_quality(
            self.usecase_agent,
            input_data=feature_payload,
            base_name=base_name.replace(
                "feature_setup_template", "usecase_detect_template"
            ),
            iteration=iteration,
            agent_history=agent_history,
            parent_event_id=feature_event.event_id,
        )
        usecase_payload = usecase_event.payload

        industry_event = self._run_with_quality(
            self.industry_agent,
            input_data=usecase_payload,
            base_name=base_name.replace(
                "usecase_detect_template", "industry_class_template"
            ),
            iteration=iteration,
            agent_history=agent_history,
            parent_event_id=usecase_event.event_id,
        )
        industry_payload = industry_event.payload

        company_event = self._run_with_quality(
            self.company_agent,
            input_data=industry_payload,
            base_name=base_name.replace(
                "industry_class_template", "company_assign_template"
            ),
            iteration=iteration,
            agent_history=agent_history,
            parent_event_id=industry_event.event_id,
        )

        return company_event
