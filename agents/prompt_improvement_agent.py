"""
prompt_improvement_agent.py

Purpose : Agent to iteratively improve prompt definitions based on feedback from quality and controller agents.
Version : 1.2.0
Author  : Konstantin & AI Copilot
Notes   :
- Applies improvement heuristics or LLM-driven rewrite (plug-in ready)
- Receives prompt text, feedback, and meta/context info
- Returns AgentEvent with improved prompt and rationale
- Handles prompt_version increment (done by runner)
- Log-ready, Pydantic contract
"""

from utils.schema import AgentEvent
from datetime import datetime


class PromptImprovementAgent:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client  # Optional, for LLM-driven rewrite

    def run(
        self,
        prompt_text: str,
        feedback: str,
        base_name: str,
        iteration: int,
        prompt_version: str,
        meta=None,
    ) -> AgentEvent:
        improved_prompt, rationale = self._improve_prompt(prompt_text, feedback)
        payload = {
            "improved_prompt": improved_prompt,
            "rationale": rationale,
            "previous_version": prompt_version,
            "feedback": feedback,
        }
        return AgentEvent(
            event_type="prompt_improvement",
            agent_name="PromptImprovementAgent",
            agent_version="1.2.0",
            timestamp=datetime.utcnow(),
            step_id=f"improve_{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )

    def _improve_prompt(self, prompt_text: str, feedback: str) -> (str, str):
        # Simple heuristic: Append feedback as TODO if LLM not used
        if not feedback:
            rationale = "No feedback provided; no changes applied."
            return prompt_text, rationale

        # If LLM client provided, use it to rewrite
        if self.llm_client:
            improved = self.llm_client.rewrite_prompt(prompt_text, feedback)
            rationale = "LLM rewrite applied based on feedback."
            return improved, rationale

        # Else, append feedback as a TODO at the end (simple baseline)
        improved_prompt = (
            prompt_text
            + "\n\n# TODO (auto): The following improvements are suggested:\n"
            + feedback
        )
        rationale = "Feedback appended as TODO; manual adjustment required."
        return improved_prompt, rationale
