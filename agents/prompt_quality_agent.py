"""
agents/prompt_quality_agent.py

Purpose : Evaluates prompt quality holistically based on the current and all previous domain agent outputs.
Logging : All evaluation events (success and error) are appended to a workflow-centric JSONL log using JsonlEventLogger.

Version : 2.2.0
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
    suggest_improvement_for: str | None = (
        None  # Name des vorherigen Agents, falls Rücksprung empfohlen
    )


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
        input_data,  # Aktueller Agent-Output (z.B. das Step-Output als dict)
        agent_history=None,  # Liste aller bisherigen Agentenoutputs (optional, als Kontext für holistische Bewertung)
        base_name: str = "",
        iteration: int = 1,
        workflow_id: str = None,
        parent_event_id: str = None,
    ):
        if workflow_id is None:
            from utils.time_utils import timestamp_for_filename

            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            input_json_str = json.dumps(input_data, ensure_ascii=False, indent=2)
            history_json_str = (
                json.dumps(agent_history, ensure_ascii=False, indent=2)
                if agent_history
                else "[]"
            )

            # Holistischer Bewertungs-Prompt:
            prompt = (
                "You are an autonomous prompt quality reviewer for a multi-step AI workflow.\n"
                "Evaluate not only the current agent output, but also the combined sequence of all previous outputs and their feedback.\n"
                "Your decision criteria:\n"
                "- Should the workflow continue? Did all steps so far deliver sufficient quality *in combination*?\n"
                "- If you PASS, always provide at least one concrete improvement suggestion for the pipeline.\n"
                "- If you FAIL, state which prior step/agent should be improved and why.\n"
                "- Never refer to hard thresholds or fixed rules; always decide dynamically.\n"
                "- Output must be a valid JSON object with: score (0.0–1.0), passed (bool), feedback (string), and suggest_improvement_for (string|null).\n\n"
                f"Workflow history (all previous agent outputs):\n{history_json_str}\n\n"
                f"Current agent output to review:\n{input_json_str}\n"
                "Respond ONLY with the JSON object. No explanations or comments."
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
                "agent_history": agent_history,
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="prompt_quality_evaluation",
                agent_name="PromptQualityAgent",
                agent_version="2.2.0",
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
                agent_version="2.2.0",
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
