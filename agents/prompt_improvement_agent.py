"""
agents/prompt_improvement_agent.py

Purpose : Improves prompts based on feedback from quality evaluations (per domain agent or holistic pipeline context).
Logging : All improvement events (success and error) are appended to a workflow-centric JSONL log using JsonlEventLogger.

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


class PromptImprovementAgent:
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
        agent_history: list = None,  # NEU: History als Kontext für gezielte Verbesserungen
    ):
        if workflow_id is None:
            from utils.time_utils import timestamp_for_filename

            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # History als Kontext nutzbar machen (z. B. Verbesserung Step X)
            improvement_context = ""
            if agent_history is not None:
                improvement_context = (
                    "\n\nFull pipeline context/history so far (JSON):\n"
                    + json.dumps(agent_history, indent=2)
                )

            input_json_str = json.dumps(input_data, indent=2)
            prompt = (
                f"You are a prompt improvement engine."
                f"\nBased on the following prompt and feedback, create an improved prompt."
                f"\nPrompt and feedback JSON:\n{input_json_str}"
                f"{improvement_context}"
                "\n\nRespond ONLY with the improved prompt text."
                "\nDo NOT include explanations or extra text."
            )
            response = self.llm.chat(prompt=prompt)
            print("🧠 LLM Response:\n", response)

            improved_prompt_text = response.strip()

            # Ensure JSON output instruction is retained. Downstream agents expect JSON.
            if "json" not in improved_prompt_text.lower():
                improved_prompt_text += "\nRespond only with valid JSON."

            # Robust fallback: No apologies, no empty, fallback to original prompt
            apology_phrases = (
                "i'm sorry",
                "i am sorry",
                "sorry",
                "es tut mir leid",
            )
            if not improved_prompt_text or improved_prompt_text.lower().startswith(
                apology_phrases
            ):
                original_prompt = input_data.get("original_prompt", "")
                if original_prompt:
                    improved_prompt_text = original_prompt

            payload = {
                "improved_prompt": improved_prompt_text,
                "input_data": input_data,
                "improvement_context": (
                    agent_history if agent_history is not None else []
                ),
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="prompt_improvement",
                agent_name="PromptImprovementAgent",
                agent_version="2.2.0",
                timestamp=cet_now(),
                step_id="prompt_improvement",
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
                agent_name="PromptImprovementAgent",
                agent_version="2.2.0",
                timestamp=cet_now(),
                step_id="prompt_improvement",
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
