"""
controller_agent.py

Purpose : Supervises the prompt lifecycle by aligning agent outputs, making retry/abort/continue decisions.
Version : 1.1.2
Author  : Konstantin & AI Copilot
Notes   :
- Accepts scoring matrix type as explicit Enum for max type safety.
- Logs all controller events exclusively to logs/weighted_score/
- May use scoring matrix in future for custom decision policies.
- Core output is an AgentEvent with controller action ("retry", "abort", "continue").
"""

from typing import Dict, Any, Optional
from datetime import datetime
from utils.scoring_matrix_types import ScoringMatrixType
from utils.schema import AgentEvent
from utils.event_logger import write_event_log
from pathlib import Path

LOG_DIR = Path("logs") / "weighted_score"


class ControllerAgent:
    def __init__(
        self,
        scoring_matrix_type: Optional[ScoringMatrixType] = None,
        openai_client: Optional[Any] = None,
    ):
        self.agent_name = "ControllerAgent"
        self.agent_version = "1.1.2"
        self.scoring_matrix_type = scoring_matrix_type
        self.openai_client = openai_client

    def run(
        self,
        improved_prompt: str,
        feedback: str,
        base_name: str,
        iteration: int,
        prompt_version: str = None,
        meta: Dict[str, Any] = None,
    ) -> AgentEvent:
        action = self.controller_decision(feedback)
        payload = {
            "action": action,
            "feedback": feedback,
        }
        event = AgentEvent(
            event_type="controller_decision",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )
        write_event_log(event)
        return event

    def controller_decision(self, feedback: str) -> str:
        # TODO: Extend with real LLM/heuristic; for now: abort if "fatal" in feedback, else retry
        if "fatal" in feedback.lower():
            return "abort"
        return "retry"
