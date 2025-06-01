"""
CompanyMatchAgent

Matches suitable companies for a given article/use case/industry classification.
Returns all results as an AgentEvent with CompanyMatchResult as payload.

Notes:
------
- Supports different matching methods (vector search, external APIs, etc.).
- For now: example implementation with LLM and placeholder for database/API.
- Modular and easy to extend with new data sources, scoring logic, etc.
"""

from typing import Any, Dict, List
from agents.utils.schemas import AgentEvent, BaseModel, Field


class CompanyMatchResult(BaseModel):
    """
    Result schema for company matchmaking.
    """

    companies: List[Dict[str, Any]] = Field(
        ...,
        description="List of suggested companies [{'name': str, 'id': str, 'score': float, ...}]",
    )
    source: str = Field(..., description="Source(s) used for company matching")
    confidence: float = Field(..., description="Confidence score (0..1)")
    rationale: str = Field(
        ..., description="Explanation/rationale for company selection"
    )


class CompanyMatchAgent:
    def __init__(
        self, openai_client, agent_name="CompanyMatchAgent", agent_version="1.0"
    ):
        self.openai = openai_client
        self.agent_name = agent_name
        self.agent_version = agent_version

    def run(
        self,
        industry_classes: List[Dict[str, Any]],
        usecases: List[str],
        features: List[str],
        prompt_template: str,
        prompt_version: str = None,
        meta: dict = None,
        method: str = "llm",
    ) -> AgentEvent:
        """
        Suggest companies based on classification/usecases/features.
        Returns an AgentEvent with CompanyMatchResult.
        """
        meta = meta or {}
        companies, source, confidence, rationale = self._match_with_llm(
            industry_classes, usecases, features, prompt_template
        )
        result = CompanyMatchResult(
            companies=companies,
            source=source,
            confidence=confidence,
            rationale=rationale,
        )
        event = AgentEvent(
            event_type="company_match",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            step_id=meta.get("step_id", ""),
            prompt_version=prompt_version,
            meta=meta,
            payload=result.dict(),
        )
        return event

    def _match_with_llm(self, industry_classes, usecases, features, prompt_template):
        """
        Use OpenAI LLM to suggest companies based on provided information.
        """
        system_prompt = (
            "You are a B2B market intelligence analyst. Based on the industry classification, use cases, and features below, "
            "suggest real-world companies that could be potential buyers. Each suggestion should have a company name, identifier (if possible), and a relevance score (0..1).\n\n"
            f"Industry Classes: {industry_classes}\n"
            f"Use Cases: {usecases}\n"
            f"Features: {features}\n\n"
            f"Matching Prompt Template:\n{prompt_template}\n\n"
            "Respond in valid JSON:\n"
            '{"companies": [{"name": str, "id": str, "score": float}], "source": str, "confidence": float, "rationale": str}\n'
        )
        response = self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=800,
            temperature=0.3,
        )
        content = response.choices[0].message.content
        try:
            result = (
                eval(content)
                if content.strip().startswith("{")
                else {"companies": [], "source": "", "confidence": 0.0, "rationale": ""}
            )
            companies = result.get("companies", [])
            source = result.get("source", "")
            confidence = result.get("confidence", 0.0)
            rationale = result.get("rationale", "")
        except Exception:
            companies, source, confidence, rationale = [], "", 0.0, ""
        return companies, source, confidence, rationale
