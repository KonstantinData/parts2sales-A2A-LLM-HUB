"""
prompt_improvement_agent.py

Purpose : Improves prompts using LLM feedback and weighted rationale. Receives OpenAIClient via Dependency Injection.
Version : 1.3.1
Author  : Konstantin’s AI Copilot
Notes   :
- Returns AgentEvent with correct fields for event logging.
"""

from typing import Any
from pathlib import Path
from datetime import datetime
from utils.openai_client import OpenAIClient
from utils.schemas import AgentEvent


class PromptImprovementAgent:
    def __init__(self, openai_client: OpenAIClient):
        self.llm = openai_client

    def run(
        self, prompt_path: Path, feedback: str, base_name: str = "", iteration: int = 1
    ) -> AgentEvent:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_content = f.read()
        llm_response = self.llm.chat_completion(
            prompt=f"{prompt_content}\n\nFeedback for improvement:\n{feedback}"
        )
        first_message = (
            llm_response.choices[0].message["content"]
            if llm_response.choices and "content" in llm_response.choices[0].message
            else ""
        )
        updated_prompt = first_message
        updated_path = prompt_path
        payload = {
            "llm_output": first_message,
            "updated_prompt": updated_prompt,
            "feedback_used": feedback,
        }
        meta = {
            "updated_path": str(updated_path),
            "iteration": iteration,
        }
        event = AgentEvent(
            event_type="prompt_improvement",
            agent_name="PromptImprovementAgent",
            agent_version="1.3.1",
            timestamp=datetime.utcnow(),
            step_id="prompt_improvement",
            prompt_version=base_name,
            status="success",
            payload=payload,
            meta=meta,
        )
        return event
