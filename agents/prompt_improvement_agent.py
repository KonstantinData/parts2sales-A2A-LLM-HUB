"""
agents/prompt_improvement_agent.py

Purpose : Improves prompts based on feedback from quality evaluations.
Logging : All improvement events (success and error) are appended to a workflow-centric JSONL log using JsonlEventLogger.

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
    ):
        if workflow_id is None:
            from utils.time_utils import timestamp_for_filename

            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            input_json_str = json.dumps(input_data)
            prompt = (
                f"You are a prompt improvement engine.\n"
                f"Based on the following prompt and feedback, create an improved prompt.\n\n"
                f"Prompt and feedback JSON:\n{input_json_str}\n\n"
                "Respond ONLY with the improved prompt text.\n"
                "Do NOT include explanations or extra text."
            )
            response = self.llm.chat(prompt=prompt)
            print("🧠 LLM Response:\n", response)

            improved_prompt_text = response.strip()

            # If the LLM answered with an apology or empty text, fall back to the
            # original prompt. This prevents downstream agents from receiving an
            # invalid prompt like "I'm sorry..." which would cause parsing errors.
            apology_phrases = (
                "i'm sorry",
                "i am sorry",
                "sorry",
                "es tut mir leid",
            )
            if not improved_prompt_text or improved_prompt_text.lower().startswith(apology_phrases):
                original_prompt = input_data.get("original_prompt", "")
                if original_prompt:
                    improved_prompt_text = original_prompt

            payload = {
                "improved_prompt": improved_prompt_text,
                "input_data": input_data,
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="prompt_improvement",
                agent_name="PromptImprovementAgent",
                agent_version="2.1.0",
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
                agent_version="2.1.0",
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
