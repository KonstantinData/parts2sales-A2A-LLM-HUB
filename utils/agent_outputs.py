"""
utils/agent_outputs.py

Purpose : Pydantic output schemas for standardized agent outputs.
Version : 2.0.0
Author  : Konstantin Milonas with Agentic AI Copilot support
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List


class FeatureExtractionOutput(BaseModel):
    features_extracted: Dict[str, Any] = Field(
        ..., description="Dictionary of features extracted from the input."
    )


class QualityEvaluationOutput(BaseModel):
    passed: bool = Field(..., description="Did the prompt pass the quality threshold?")
    feedback: str = Field(..., description="LLM or agent feedback.")
    detailed_feedback: str = Field(
        ..., description="LLM detailed improvement advice, if applicable."
    )


class UsecaseDetectionOutput(BaseModel):
    application_domains: List[str] = Field(
        ..., description="List of inferred application or usage domains."
    )


class IndustryClassificationOutput(BaseModel):
    industry_sectors: List[str] = Field(
        ..., description="List of detected industry sectors."
    )


class CompanyMatchOutput(BaseModel):
    matched_companies: List[str] = Field(
        ..., description="List of matched company names or IDs."
    )


class ContactMatchOutput(BaseModel):
    matched_contacts: List[str] = Field(
        ..., description="List of matched contact names, emails, or IDs."
    )


class CrmSyncOutput(BaseModel):
    synced_companies_count: int = Field(
        ..., description="Count of companies synced to CRM."
    )
    synced_contacts_count: int = Field(
        ..., description="Count of contacts synced to CRM."
    )
    message: str = Field(..., description="Sync status or summary.")


class CostMonitorOutput(BaseModel):
    total_tokens: int = Field(..., description="Total OpenAI tokens used.")
    total_cost_usd: float = Field(
        ..., description="Total estimated USD cost for API usage."
    )
