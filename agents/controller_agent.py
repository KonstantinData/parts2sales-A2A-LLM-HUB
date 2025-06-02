"""
controller_agent.py

Purpose : Central coordination agent to decide workflow actions (continue, retry, abort)
          after each prompt improvement cycle, based on feedback and current state.
Version : 1.2.0
Author  : Konstantin & AI Copilot
Notes   :
- Receives improved prompt and meta info after each cycle
- Applies rule-based or LLM-based policy to trigger: 'retry', 'abort', 'accept'
- Returns AgentEvent with action and rationale
- Log-/pipeline-ready, Pydantic contract
"""

from utils.schema import AgentEvent
from datetime import datetime


class ControllerAgent:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client  # Optional for LLM-based decision logic

    def run(
        self,
        improved_prompt: str,
        feedback: str,
        base_name: str,
        iteration: int,
        prompt_version: str,
        meta=None,
    ) -> AgentEvent:
        action, rationale = self._decide(improved_prompt, feedback, iteration)
        payload = {
            "action": action,  # 'retry', 'abort', 'accept'
            "rationale": rationale,
            "feedback": feedback,
            "iteration": iteration,
        }
        return AgentEvent(
            event_type="controller_decision",
            agent_name="ControllerAgent",
            agent_version="1.2.0",
            timestamp=datetime.utcnow(),
            step_id=f"controller_{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )

    def _decide(
        self, improved_prompt: str, feedback: str, iteration: int
    ) -> (str, str):
        # Baseline policy:
        # If critical feedback or too many iterations, abort. Otherwise, retry.
        if iteration >= 3:
            return "abort", "Max iterations reached."
        if feedback and any(
            w in feedback.lower() for w in ["fatal", "error", "unfixable", "abandon"]
        ):
            return "abort", "Critical feedback: aborting."
        if not feedback or feedback.strip() == "":
            return "accept", "No feedback: improvement accepted."
        return "retry", "Feedback present: retry improvement cycle."
