"""
base_agent.py

Purpose : Abstract base class for all agents; standardizes API, versioning, and logging.
Version : 1.0.1
Author  : Konstantin & AI Copilot
Notes   :
- All agent subclasses should inherit and call super().__init__ with agent_name/version.
- Logs events exclusively to logs/weighted_score/ if log_event() is used.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from utils.schema import AgentEvent
from utils.event_logger import write_event_log
from pathlib import Path

LOG_DIR = Path("logs") / "weighted_score"


class BaseAgent:
    def __init__(
        self,
        agent_name: str,
        agent_version: str,
    ):
        self.agent_name = agent_name
        self.agent_version = agent_version

    def log_event(
        self,
        event_type: str,
        step_id: str,
        prompt_version: Optional[str],
        meta: Optional[Dict[str, Any]],
        payload: Dict[str, Any],
    ) -> AgentEvent:
        event = AgentEvent(
            event_type=event_type,
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=step_id,
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )
        write_event_log(LOG_DIR, event)
        return event
