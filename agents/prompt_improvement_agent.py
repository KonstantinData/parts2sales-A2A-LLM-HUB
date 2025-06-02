"""
agents/prompt_improvement_agent.py

Improves prompts based on feedback and target criteria.
Returns structured AgentEvent objects for agentic workflows.

# Notes:
- Supports creative_mode flag for exploratory improvements.
- Designed for extension with LLM calls or heuristic logic.
"""

from agents.utils.schemas import AgentEvent


class PromptImprovementAgent:
    def __init__(
        self,
        openai_client=None,
        creative_mode=False,
        agent_name="PromptImprovementAgent",
        agent_version="1.0",
    ):
        self.openai = openai_client
        self.creative_mode = creative_mode
        self.agent_name = agent_name
        self.agent_version = agent_version

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
        rationale = f"Applied feedback: {feedback}. Creative mode: {self.creative_mode}"

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
