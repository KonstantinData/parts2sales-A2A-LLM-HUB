"""
IndustryClassAgent

Classifies article features/use cases into industry classes (e.g., NAICS, NACE, SIC).
Returns all results as an AgentEvent with IndustryClassResult as payload.

Notes:
------
- Uses OpenAI LLM for classification.
- Modular: logic can be extended to add rule-based or hybrid methods.
- Always returns standardized AgentEvent with all meta info for traceability.
"""

from typing import Any, Dict, List
from agents.utils.schemas import AgentEvent, BaseModel, Field


class IndustryClassResult(BaseModel):
    """
    Result schema for industry classification.
    """

    industry_classes: List[Dict[str, Any]] = Field(
        ...,
        description="List of assigned industry classes, e.g., [{'code': '3345', 'name': 'Electronic Component Manufacturing'}]",
    )
    confidence: float = Field(
        ..., description="Confidence score for industry assignment (0..1)"
    )
    source: str = Field(
        ..., description="Classification system used (e.g., NAICS, NACE, SIC)"
    )
    rationale: str = Field(..., description="Explanation/rationale for classification")


class IndustryClassAgent:
    def __init__(
        self, openai_client, agent_name="IndustryClassAgent", agent_version="1.0"
    ):
        self.openai = openai_client
        self.agent_name = agent_name
        self.agent_version = agent_version

    def run(
        self,
        features: List[str],
        usecases: List[str],
        prompt_template: str,
        prompt_version: str = None,
        meta: dict = None,
        method: str = "llm",
    ) -> AgentEvent:
        """
        Classify into industry classes using provided prompt template.
        Returns an AgentEvent with IndustryClassResult.
        """
        meta = meta or {}
        industry_classes, confidence, source, rationale = self._classify_with_llm(
            features, usecases, prompt_template
        )
        result = IndustryClassResult(
            industry_classes=industry_classes,
            confidence=confidence,
            source=source,
            rationale=rationale,
        )
        event = AgentEvent(
            event_type="industry_classification",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            step_id=meta.get("step_id", ""),
            prompt_version=prompt_version,
            meta=meta,
            payload=result.dict(),
        )
        return event

    def _classify_with_llm(self, features, usecases, prompt_template):
        """
        Use OpenAI LLM to assign industry classes based on features and use cases.
        """
        system_prompt = (
            "You are an industry classification expert. Given the following features and use cases, and the classification template, "
            "assign the most relevant industry classes (return as a list of dicts with 'code' and 'name'), "
            "state the classification system, give a confidence score (0..1), and explain your rationale.\n\n"
            f"Features: {features}\n"
            f"Use Cases: {usecases}\n\n"
            f"Classification Template:\n{prompt_template}\n\n"
            "Respond in valid JSON:\n"
            '{"industry_classes": [{"code": str, "name": str}], "confidence": float, "source": str, "rationale": str}\n'
        )
        response = self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=800,
            temperature=0.4,
        )
        content = response.choices[0].message.content
        try:
            result = (
                eval(content)
                if content.strip().startswith("{")
                else {
                    "industry_classes": [],
                    "confidence": 0.0,
                    "source": "",
                    "rationale": "",
                }
            )
            industry_classes = result.get("industry_classes", [])
            confidence = result.get("confidence", 0.0)
            source = result.get("source", "")
            rationale = result.get("rationale", "")
        except Exception:
            industry_classes, confidence, source, rationale = [], 0.0, "", ""
        return industry_classes, confidence, source, rationale
