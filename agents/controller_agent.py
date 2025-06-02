"""
ControllerAgent

Controls the improvement workflow by deciding whether to retry, continue, or abort
based on the improved prompt and feedback.
Always returns structured AgentEvent objects.
Ready for plug-and-play extension.
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
        improved_prompt: str,
        feedback: str,
        base_name: str,
        iteration: int,
        prompt_version: str = None,
        meta: dict = None,
    ) -> AgentEvent:
        """
        Decide next action based on improved prompt and feedback.
        Returns AgentEvent with action in payload: 'retry', 'continue', or 'abort'.
        """
        meta = meta or {}

        # Simple logic: if "IMPROVED" is present and iteration < 3, retry once, then continue.
        if "IMPROVED" in improved_prompt and iteration < 2:
            action = "retry"
            rationale = "Requesting another improvement iteration."
        elif iteration >= 3:
            action = "abort"
            rationale = "Max iterations reached."
        else:
            action = "continue"
            rationale = "Prompt meets minimal improvement criteria."

        payload = {
            "action": action,
            "rationale": rationale,
            "prompt_version": prompt_version,
        }

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
