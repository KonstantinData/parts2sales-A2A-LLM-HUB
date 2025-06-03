"""
controller_agent.py

Purpose : Supervises the prompt lifecycle by aligning agent outputs, making retry/abort/continue decisions. Receives OpenAIClient via Dependency Injection.
Version : 1.3.1
Author  : Konstantin’s AI Copilot
Notes   :
- Returns AgentEvent with correct fields for event logging.
"""

from typing import Any, Optional
from datetime import datetime
from utils.openai_client import OpenAIClient
from utils.schemas import AgentEvent


class ControllerAgent:
    def __init__(self, openai_client: OpenAIClient):
        self.llm = openai_client

    def run(self, pq_event: Any, pi_event: Optional[Any] = None) -> AgentEvent:
        retry = False
        action = "continue"
        if (
            pq_event
            and pq_event.payload
            and not pq_event.payload.get("pass_threshold", True)
        ):
            retry = True
            action = "retry"
        payload = {
            "retry": retry,
            "action": action,
        }
        meta = {
            "prompt_quality_id": getattr(pq_event, "meta", {}).get("log_id"),
            "prompt_improvement_id": (
                getattr(pi_event, "meta", {}).get("log_id") if pi_event else None
            ),
        }
        event = AgentEvent(
            event_type="controller_decision",
            agent_name="ControllerAgent",
            agent_version="1.3.1",
            timestamp=datetime.utcnow(),
            step_id="controller_decision",
            prompt_version=getattr(pq_event, "prompt_version", ""),
            status="success",
            payload=payload,
            meta=meta,
        )
        return event
