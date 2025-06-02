"""
schema.py

Purpose : Central Pydantic schemas for all agent events and payloads.
Version : 1.0.0
Author  : Konstantin & AI Copilot
Notes   :
- All agent interactions and logs use AgentEvent as the base contract.
- Supports strict typing, extensibility, and traceability across all workflow steps.
- Contains specialized payload classes (e.g., PromptQualityResult) as needed.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class PromptQualityResult(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    matrix: Dict[str, float]
    feedback: str
    pass_threshold: bool
    issues: List[str] = Field(default_factory=list)
    prompt_version: Optional[str] = None


class AgentEvent(BaseModel):
    event_type: str
    agent_name: str
    agent_version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    step_id: str
    prompt_version: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    payload: Dict[str, Any]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
