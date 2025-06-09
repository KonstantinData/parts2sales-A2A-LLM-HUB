"""
utils/schemas.py

Purpose : Defines event schemas for agent logging and contracts.
Version : 2.0.0
Author  : Konstantin Milonas with Agentic AI Copilot support
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime


class AgentEvent(BaseModel):
    event_id: str = Field(..., description="Unique identifier for this event.")
    event_type: str = Field(
        ..., description="Type of event (e.g., extraction, scoring, error, etc.)."
    )
    agent_name: str = Field(..., description="Name of the agent emitting this event.")
    agent_version: str = Field(..., description="Version of the agent.")
    timestamp: datetime = Field(..., description="Event creation timestamp (ISO).")
    step_id: str = Field(..., description="Logical step identifier.")
    prompt_version: Optional[str] = Field(
        None, description="Prompt file version or base name."
    )
    status: str = Field(..., description="Event status (success, error, etc.).")
    payload: Dict[str, Any] = Field(
        ..., description="Arbitrary event-specific content."
    )
    meta: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Meta/auxiliary event data."
    )
    workflow_id: Optional[str] = Field(
        None, description="ID of workflow this event belongs to."
    )
    source_event_id: Optional[str] = Field(
        None, description="EventID of parent/source event (for chaining)."
    )
