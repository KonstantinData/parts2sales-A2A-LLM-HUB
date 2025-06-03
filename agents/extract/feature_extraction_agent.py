"""
feature_extraction_agent.py

Purpose : Extracts product features using a dedicated scoring matrix and LLM. Receives OpenAIClient via Dependency Injection.
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


class FeatureExtractionAgent:
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
            "extracted_features": first_message,
        }
        meta = {
            "base_name": base_name,
            "iteration": iteration,
        }
        event = AgentEvent(
            event_type="feature_extraction",
            agent_name="FeatureExtractionAgent",
            agent_version="1.3.1",
            timestamp=datetime.utcnow(),
            step_id="feature_extraction",
            prompt_version=base_name,
            status="success",
            payload=payload,
            meta=meta,
        )
        return event
