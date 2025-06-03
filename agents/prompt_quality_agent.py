"""
prompt_quality_agent.py

Purpose : Evaluates prompt quality using scoring matrix logic and LLM. Receives OpenAIClient via Dependency Injection.
Version : 1.3.1
Author  : Konstantin’s AI Copilot
Notes   :
- Returns AgentEvent with event_type, agent_name, agent_version, timestamp, step_id, prompt_version, status, payload, meta.
"""

from typing import Any
from pathlib import Path
from datetime import datetime
from utils.openai_client import OpenAIClient
from utils.schemas import AgentEvent
from utils.scoring_matrix_types import ScoringMatrixType


class PromptQualityAgent:
    def __init__(
        self, scoring_matrix_type: ScoringMatrixType, openai_client: OpenAIClient
    ):
        self.scoring_matrix_type = scoring_matrix_type
        self.llm = openai_client

    def run(self, prompt_path: Path, base_name: str, iteration: int) -> AgentEvent:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_content = f.read()
        llm_response = self.llm.chat_completion(prompt=prompt_content)
        first_message = (
            llm_response.choices[0].message["content"]
            if llm_response.choices and "content" in llm_response.choices[0].message
            else ""
        )
        payload = {
            "llm_output": first_message,
            "pass_threshold": False,
            "feedback": "",
        }
        event = AgentEvent(
            event_type="quality_check",
            agent_name="PromptQualityAgent",
            agent_version="1.3.1",
            timestamp=datetime.utcnow(),
            step_id="quality_evaluation",
            prompt_version=base_name,
            status="success",
            payload=payload,
            meta={
                "iteration": iteration,
                "scoring_matrix_type": self.scoring_matrix_type.name,
            },
        )
        return event
