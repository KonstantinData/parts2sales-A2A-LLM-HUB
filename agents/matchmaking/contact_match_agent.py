"""
contact_match_agent.py

Purpose : Matches contacts using LLM and scoring matrix. Receives OpenAIClient via Dependency Injection.
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


class ContactMatchAgent:
    def __init__(self, openai_client: OpenAIClient):
        self.llm = openai_client

    def run(
        self, prompt_path: Path, base_name: str = "", iteration: int = 1
    ) -> AgentEvent:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_content = f.read()
        llm_response = self.llm.chat_completion(prompt=prompt_content)
        first_message = (
            llm_response.choices[0].message["content"]
            if llm_response.choices and "content" in llm_response.choices[0].message
            else ""
        )
        payload = {
            "matched_contacts": first_message,
        }
        meta = {
            "base_name": base_name,
            "iteration": iteration,
        }
        event = AgentEvent(
            event_type="contact_matching",
            agent_name="ContactMatchAgent",
            agent_version="1.3.1",
            timestamp=datetime.utcnow(),
            step_id="contact_matching",
            prompt_version=base_name,
            status="success",
            payload=payload,
            meta=meta,
        )
        return event
