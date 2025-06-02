"""
agents/controller_agent.py

Controller agent for decision making in prompt workflows.
Analyzes improvement feedback and decides on retry or abort.

# Notes:
- Returns structured AgentEvent with action payload.
- Designed for pluggable decision logic.
"""

from agents.utils.schemas import AgentEvent


class ControllerAgent:
    def __init__(
        self,
        client=None,
        agent_name="ControllerAgent",
        agent_version="1.0",
    ):
        self.client = client
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

        # Simple heuristic: retry if feedback contains "improvement"
        action = "retry" if "improvement" in feedback.lower() else "abort"

        payload = {"action": action}

        event = AgentEvent(
            event_type="controller_decision",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            step_id=f"{base_name}_iter{iteration}",
            prompt_version=prompt_version,
            meta=meta,
            payload=payload,
        )
        return event
