# utils/agent_outputs.py

from pydantic import BaseModel, Field
from typing import Dict, Any


class FeaturesExtracted(BaseModel):
    """Schema for structured output of the FeatureExtractionAgent."""

    features_extracted: Dict[str, Any] = Field(
        ..., description="Dictionary of extracted features from the input content."
    )


class QualityEvaluation(BaseModel):
    """Schema for structured evaluation results of PromptQualityAgent."""

    score: float = Field(
        ..., ge=0.0, le=1.0, description="Quality score between 0 and 1."
    )
    passed: bool = Field(..., description="Whether the quality threshold was met.")
    feedback: str = Field(..., description="Feedback explaining the score decision.")
