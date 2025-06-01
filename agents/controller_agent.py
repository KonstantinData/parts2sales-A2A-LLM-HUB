"""
ControllerAgent

Agent to decide workflow actions based on event results.
Evaluates if an improved prompt meets requirements, should retry, or aborts the loop.
Always returns an AgentEvent with ControllerResult as payload.

Notes:
------
- Alignment scoring may be rule-based or LLM-based (here: simple heuristic).
- Used to control loop/retry logic in agentic prompt improvement workflows.
- All workflow branching is centralized via this agent.
"""

from typing import Any, Dict
from agents.utils.schemas import AgentEvent, ControllerResult


class ControllerAgent:
    def __init__(self, agent_name="ControllerAgent", agent_version="1.0"):
        self.agent_name = agent_name
        self.agent_version = agent_version

    def run(
        self,
        improved_prompt: str,
        previous_feedback: Dict[str, Any],
        prompt_version: str = None,
        meta: dict = None,
        method: str = "simple",
    ) -> AgentEvent:
        """
        Decide workflow action based on improved prompt and feedback.
        Returns an AgentEvent with ControllerResult.
        """
        meta = meta or {}

        alignment_score, rationale = self._alignment_check(
            improved_prompt, previous_feedback
        )
        # Simple rule: pass if score > 0.85, else retry, abort if score < 0.4
        if alignment_score >= 0.85:
            action = "pass"
        elif alignment_score >= 0.4:
            action = "retry"
        else:
            action = "abort"

        result = ControllerResult(
            action=action,
            alignment_score=alignment_score,
            rationale=rationale,
            details={"meta": meta, "prompt_version": prompt_version},
        )

        event = AgentEvent(
            event_type="controller_decision",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            step_id=meta.get("step_id", ""),
            prompt_version=prompt_version,
            meta=meta,
            payload=result.dict(),
        )
        return event

    def _alignment_check(self, improved_prompt: str, previous_feedback: Dict[str, Any]):
        """
        Dummy: Alignment score is high if feedback words are present in improved prompt.
        """
        feedback = previous_feedback.get("feedback", "")
        if not feedback:
            return 1.0, "No feedback given; prompt passes by default."
        # Check overlap (could use more advanced NLP/LLM)
        present = sum(word in improved_prompt for word in feedback.split())
        total = len(feedback.split())
        if total == 0:
            return 1.0, "No feedback to align with."
        alignment_score = present / total
        rationale = f"Alignment based on feedback keyword presence ({present}/{total})."
        return alignment_score, rationale
