"""
UsecaseDetectionAgent

Detects and suggests relevant use cases based on article features and prompt template.
Returns all results as an AgentEvent with UsecaseDetectionResult as payload.

Notes:
------
- Uses OpenAI LLM for semantic use-case detection.
- Fully modular for future extension (add more fields, decision logic, etc.).
"""

from typing import Any, Dict, List
from agents.utils.schemas import AgentEvent, BaseModel, Field


class UsecaseDetectionResult(BaseModel):
    """
    Result schema for use case detection.
    """

    usecases: List[str] = Field(
        ..., description="Detected use cases for the article/features"
    )
    confidence: float = Field(
        ..., description="Confidence score for the use case assignment (0..1)"
    )
    features: List[str] = Field(
        [], description="Features on which the use cases are based"
    )
    notes: str = Field(
        "", description="Additional notes or rationale for detected use cases"
    )


class UsecaseDetectionAgent:
    def __init__(
        self, openai_client, agent_name="UsecaseDetectionAgent", agent_version="1.0"
    ):
        self.openai = openai_client
        self.agent_name = agent_name
        self.agent_version = agent_version

    def run(
        self,
        features: List[str],
        usecase_prompt_template: str,
        prompt_version: str = None,
        meta: dict = None,
        method: str = "llm",
    ) -> AgentEvent:
        """
        Detect use cases from extracted features using provided prompt template.
        Returns an AgentEvent with UsecaseDetectionResult.
        """
        meta = meta or {}
        usecases, confidence, notes = self._detect_with_llm(
            features, usecase_prompt_template
        )
        result = UsecaseDetectionResult(
            usecases=usecases, confidence=confidence, features=features, notes=notes
        )
        event = AgentEvent(
            event_type="usecase_detection",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            step_id=meta.get("step_id", ""),
            prompt_version=prompt_version,
            meta=meta,
            payload=result.dict(),
        )
        return event

    def _detect_with_llm(self, features, prompt_template):
        """
        Use OpenAI LLM to detect use cases for the provided features.
        """
        system_prompt = (
            "You are a domain expert for product application analysis. Given the features below and the use case template, "
            "suggest relevant use cases (as a Python list of strings), a confidence score (0..1), and rationale/notes.\n\n"
            f"Features: {features}\n\n"
            f"Use Case Prompt Template:\n{prompt_template}\n\n"
            "Respond in valid JSON:\n"
            '{"usecases": [str], "confidence": float, "notes": str}\n'
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
                else {"usecases": [], "confidence": 0.0, "notes": ""}
            )
            usecases = result.get("usecases", [])
            confidence = result.get("confidence", 0.0)
            notes = result.get("notes", "")
        except Exception:
            usecases, confidence, notes = [], 0.0, ""
        return usecases, confidence, notes
