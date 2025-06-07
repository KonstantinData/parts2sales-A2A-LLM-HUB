"""
schemas.py

Purpose : Central Pydantic schemas for all agent events and payloads.
Version : 1.2.0
Author  : Konstantin & AI Copilot
Notes   :
- All agent interactions and logs use AgentEvent as the base contract.
- Supports strict typing, extensibility, and traceability across all workflow steps.
- Contains specialized payload classes (e.g., PromptQualityResult) as needed.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from .time_utils import cet_now


class PromptQualityResult(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    matrix: Dict[str, float]
    feedback: str
    pass_threshold: bool
    issues: List[str] = Field(default_factory=list)
    prompt_version: Optional[str] = None


class FeatureExtractionResult(BaseModel):
    features_extracted: Dict[str, Any]
    feedback: str
    pass_threshold: bool
    prompt_version: Optional[str] = None


class UsecaseDetectionResult(BaseModel):
    detected_usecases: List[str]
    feedback: str
    pass_threshold: bool
    prompt_version: Optional[str] = None


class IndustryClassResult(BaseModel):
    industry_classes: List[str]
    feedback: str
    pass_threshold: bool
    prompt_version: Optional[str] = None


class CompanyMatchResult(BaseModel):
    matched_companies: List[str]
    feedback: str
    pass_threshold: bool
    prompt_version: Optional[str] = None


class ContactMatchResult(BaseModel):
    matched_contacts: List[str]
    feedback: str
    pass_threshold: bool
    prompt_version: Optional[str] = None


class RawPrompt(BaseModel):
    """Schema for raw YAML prompts."""

    id: str
    version: str
    role: str
    objective: str
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[List[str]] = None


class AgentEvent(BaseModel):
    event_type: str
    agent_name: str
    agent_version: str
    timestamp: datetime = Field(default_factory=cet_now)
    step_id: str
    prompt_version: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    status: str = "success"  # <--- added for compatibility with agents
    payload: Dict[str, Any]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
