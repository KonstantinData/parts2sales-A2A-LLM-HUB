"""
PromptImprovementAgent

This agent improves prompt templates based on feedback and target criteria.
It supports agentic workflows and always returns structured AgentEvent objects.

# Notes:
# - Designed for integration into evaluation-improvement loops.
# - Returns Pydantic-validated AgentEvent for structured logging and downstream processing.
"""

from agents.utils.schemas import AgentEvent


class PromptImprovementAgent:
    def __init__(self):
        self.agent_name = "PromptImprovementAgent"
        self.agent_version = "1.0"

    def run(
        self,
        prompt_text: str,
        feedback: str,
        base_name: str,
        iteration: int,
        prompt_version: str = None,
        meta: dict = None,
    ) -> AgentEvent:
        meta = meta or {}

        improved_prompt = prompt_text + f"\n# IMPROVED (iteration {iteration})"
        rationale = f"Applied feedback: {feedback}."

        payload = {
            "improved_prompt": improved_prompt,
            "rationale": rationale,
            "prompt_version": prompt_version,
        }

        event = AgentEvent(
            event_type="prompt_improvement",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            step_id=f"{base_name}_iter{iteration}",
            prompt_version=prompt_version,
            meta=meta,
            payload=payload,
        )
        return event
