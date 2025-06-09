"""
agents/prompt_quality_agent.py

Purpose : Evaluates prompt quality based on extracted features and domain agent outputs.
Logging : All evaluation events (success and error) are appended to a workflow-centric JSONL log using JsonlEventLogger.

Version : 2.1.0
Author  : Konstantin Milonas with Agentic AI Copilot support
"""

from pathlib import Path
from uuid import uuid4
import json
import re

from pydantic import BaseModel, ValidationError
from utils.time_utils import cet_now
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient


class QualityEvaluation(BaseModel):
    """Schema for structured evaluation results of PromptQualityAgent."""

    score: float
    passed: bool
    feedback: str


class PromptQualityAgent:
    def __init__(
        self,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        self.llm = openai_client
        self.log_dir = log_dir

    def run(
        self,
        input_data,
        base_name: str,
        iteration: int,
        workflow_id: str = None,
        parent_event_id: str = None,
    ):
        if workflow_id is None:
            from utils.time_utils import timestamp_for_filename

            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            input_json_str = json.dumps(input_data)
            prompt = (
                f"Evaluate the quality of the following prompt output (JSON):\n\n"
                f"{input_json_str}\n\n"
                "Return a JSON object with fields: score (0.0-1.0), passed (bool), feedback (string).\n"
                "Respond ONLY with the JSON, no explanations."
            )
            response = self.llm.chat(prompt=prompt)
            print("🧠 LLM Response:\n", response)

            # Extract JSON from response
            match = re.search(r"(\{.*?\})", response, re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in LLM response")
            json_str = match.group(1)
            evaluation_json = json.loads(json_str)

            validated = QualityEvaluation(**evaluation_json)

            payload = {
                "evaluation": validated.dict(),
                "input_data": input_data,
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="prompt_quality_evaluation",
                agent_name="PromptQualityAgent",
                agent_version="2.0.0",
                timestamp=cet_now(),
                step_id="prompt_quality_evaluation",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
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
                },
                workflow_id=workflow_id,
                source_event_id=parent_event_id,
            )
            logger.log_event(error_event)
            raise
