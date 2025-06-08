"""
Schemas

Version: 2.0.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Defines the unified AgentEvent structure for all logging operations.
Supports strict typing, validation, and serialization for workflow traceability.
"""

from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel


class AgentEventStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class AgentEvent(BaseModel):
    event_id: str
    agent_name: str
    agent_version: str
    event_type: str
    status: AgentEventStatus | str
    timestamp: str
    payload: Dict[str, Any]
