"""
Schemas for structured events and payloads using Pydantic.

Defines AgentEvent, PromptQualityResult, and other data contracts for
strict typing, validation, versioning, and extensibility.

# Notes:
- All event payloads extend base Pydantic models.
- Ensures consistent schema across agents and workflow.
- Includes timestamps and meta info for traceability.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class PromptQualityResult(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    matrix: Dict[str, float]
    feedback: str
    pass_threshold: bool
    issues: List[str] = []
    prompt_version: Optional[str] = None


class AgentEvent(BaseModel):
    event_type: str
    agent_name: str
    agent_version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    step_id: str
    prompt_version: Optional[str] = None
    meta: Dict[str, Any] = {}
    payload: Dict[str, Any]
