"""
Unified data models for all agent-to-agent communications.

#Notes:
- These schemas ensure that every agent returns its results in a standardized, versioned way.
- All events are the backbone of a scalable, maintainable multi-agent system.
- Extensible: Add your own agent results here.
"""

from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime


class AgentEvent(BaseModel):
    """
    #Notes:
    - Base event object for all agent communication and logging.
    - All agent actions, results, errors, and states are encapsulated in this structure.
    """

    event_type: str = Field(
        ...,
        description="Type of the event (e.g. prompt_quality, improvement, feature_extraction)",
    )
    agent_name: str = Field(
        ..., description="Name of the agent that produced this event"
    )
    agent_version: str = Field(..., description="Agent version for traceability")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Event creation timestamp",
    )
    step_id: Optional[str] = Field(None, description="Workflow step identifier")
    prompt_version: Optional[str] = Field(
        None, description="Prompt/template version used in this step"
    )
    meta: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata (iteration, file, etc.)"
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific result payload (score, feedback, improvement, etc.)",
    )


class PromptQualityResult(BaseModel):
    """
    #Notes:
    - Result schema for prompt quality evaluation.
    - Used by PromptQualityAgent and all evaluation routines.
    """

    score: float = Field(..., description="Weighted prompt quality score (0..1)")
    matrix: Dict[str, float] = Field(
        ..., description="Detailed scores for each category"
    )
    feedback: str = Field(
        ..., description="Human- or LLM-readable feedback for improvement"
    )
    pass_threshold: bool = Field(
        ..., description="If True, prompt passes minimum quality threshold"
    )
    issues: Optional[List[str]] = Field(
        default_factory=list, description="List of concrete issues or weaknesses found"
    )
    prompt_version: Optional[str] = Field(
        None, description="Prompt/template version that was evaluated"
    )


class ImprovementResult(BaseModel):
    """
    #Notes:
    - Result schema for prompt improvement.
    - Used by PromptImprovementAgent or similar.
    """

    improved_prompt: str = Field(..., description="The improved prompt text")
    rationale: str = Field(..., description="Explanation of the improvement(s) made")
    changes: Optional[List[str]] = Field(
        default_factory=list, description="Description of main changes"
    )
    prompt_version: Optional[str] = Field(
        None, description="Version of improved prompt"
    )


class ControllerResult(BaseModel):
    """
    #Notes:
    - Result schema for workflow control/decision agent.
    - Used by ControllerAgent to document alignment checks and control flow decisions.
    """

    action: str = Field(
        ..., description="Control decision: 'pass', 'retry', or 'abort'"
    )
    alignment_score: float = Field(
        ...,
        description="How well the improved prompt aligns with feedback/criteria (0..1)",
    )
    rationale: str = Field(..., description="Explanation for the action/decision")
    details: Optional[dict] = Field(
        default_factory=dict, description="Additional details or diagnostic info"
    )


# Placeholder for feature extraction agent (expand as needed)
class FeatureExtractionResult(BaseModel):
    features: List[str] = Field(..., description="Extracted features")
    confidence: Optional[float] = Field(None, description="Optional confidence score")
