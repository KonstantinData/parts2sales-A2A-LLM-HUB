"""
prompt_quality_agent.py

Purpose : Evaluates prompt features for quality using LLM scoring.
Version : 2.0.0
Author  : Konstantin Milonas with Agentic AI Copilot support
"""

from pathlib import Path
import json
from uuid import uuid4

from utils.schemas import AgentEvent
from utils.time_utils import cet_now
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient
from utils.agent_outputs import FeatureExtractionOutput


class PromptQualityAgent:
    def __init__(self, openai_client: OpenAIClient, log_dir=Path("logs/workflows")):
        self.llm = openai_client
        self.log_dir = log_dir

    def run(
        self,
        input_data: FeatureExtractionOutput,
        base_name: str,
        iteration: int,
        workflow_id: str,
        parent_event_id: str = None,
    ) -> AgentEvent:
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # Convert input for evaluation
            features_json = input_data.features_extracted
            score_prompt = (
                f"Evaluate the following extracted features for clarity and usefulness:\n\n"
                f"{json.dumps(features_json, indent=2)}\n\n"
                f'Respond with a JSON object like: {{"score": 0.0–1.0, "feedback": "..."}}'
            )

            response = self.llm.chat(prompt=score_prompt)
            result = json.loads(response)

            payload = {
                "input": features_json,
                "score": result.get("score"),
                "feedback": result.get("feedback", ""),
            }

            event = AgentEvent(
                event_type="prompt_quality",
                agent_name="PromptQualityAgent",
                agent_version="2.0.0",
                timestamp=cet_now(),
                step_id="prompt_quality_evaluation",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "retry_allowed": True,
                    "retry_count": 0,
                },
                parent_event_id=parent_event_id,
            )
            logger.log_event(event)
            return event

        except Exception as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="PromptQualityAgent",
                agent_version="2.0.0",
                timestamp=cet_now(),
                step_id="prompt_quality_evaluation",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                    "retry_allowed": True,
                    "retry_count": 0,
                },
                parent_event_id=parent_event_id,
            )
            logger.log_event(error_event)
            raise
