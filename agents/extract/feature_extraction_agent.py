"""
prompt_improvement_agent.py

Purpose : Agent for improving prompts based on LLM feedback and weighted rationale.
Version : 1.1.2
Author  : Konstantin & AI Copilot
Notes   :
- Receives meta/feedback, uses LLM for guided rewriting.
- Logs all improvement events exclusively to logs/weighted_score/
- Usage:
    agent = PromptImprovementAgent()
    agent.run(prompt_text, feedback, base_name, iteration, prompt_version)
"""

from typing import Optional, Any
from datetime import datetime
from utils.schema import AgentEvent
from utils.event_logger import write_event_log
from pathlib import Path

LOG_DIR = Path("logs") / "weighted_score"


class PromptImprovementAgent:
    def __init__(
        self,
        openai_client: Optional[Any] = None,
    ):
        self.agent_name = "PromptImprovementAgent"
        self.agent_version = "1.1.2"
        self.openai_client = openai_client

    def run(
        self,
        prompt_text: str,
        feedback: str,
        base_name: str,
        iteration: int,
        prompt_version: Optional[str] = None,
        meta: Optional[dict] = None,
    ) -> AgentEvent:
        improved, rationale = self.improve_prompt(prompt_text, feedback)
        event = AgentEvent(
            event_type="prompt_improvement",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload={
                "improved_prompt": improved,
                "rationale": rationale,
                "feedback": feedback,
            },
        )
        write_event_log(LOG_DIR, event)
        return event

    def improve_prompt(self, prompt_text: str, feedback: str):
        # Replace with actual LLM logic
        improved = prompt_text + "\n# Improved based on feedback"
        rationale = "Prompt rewritten to address feedback."
        return improved, rationale
