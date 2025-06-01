"""
FeatureExtractionAgent

Extracts relevant features from article data and prompt templates.
Returns all results as an AgentEvent with FeatureExtractionResult as payload.

Notes:
------
- Uses OpenAI LLM for feature extraction.
- Modular: logic can be extended to add rule-based or hybrid methods.
- Always returns standardized AgentEvent with all meta info for traceability.
"""

from typing import Any, Dict
from agents.utils.schemas import AgentEvent, FeatureExtractionResult


class FeatureExtractionAgent:
    def __init__(
        self, openai_client, agent_name="FeatureExtractionAgent", agent_version="1.0"
    ):
        self.openai = openai_client
        self.agent_name = agent_name
        self.agent_version = agent_version

    def run(
        self,
        article_data: dict,
        prompt_template: str,
        prompt_version: str = None,
        meta: dict = None,
        method: str = "llm",
    ) -> AgentEvent:
        """
        Extract features from article data using the provided prompt template.
        Returns an AgentEvent with FeatureExtractionResult.
        """
        meta = meta or {}
        features, confidence = self._extract_with_llm(article_data, prompt_template)
        result = FeatureExtractionResult(features=features, confidence=confidence)
        event = AgentEvent(
            event_type="feature_extraction",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            step_id=meta.get("step_id", ""),
            prompt_version=prompt_version,
            meta=meta,
            payload=result.dict(),
        )
        return event

    def _extract_with_llm(self, article_data, prompt_template):
        """
        Use OpenAI LLM to extract features based on article data and prompt template.
        """
        system_prompt = (
            "You are an expert product data analyst. Given the following article information and feature extraction template, "
            "extract the most relevant features (as a Python list of strings). "
            "If possible, estimate your confidence as a number between 0 and 1.\n\n"
            f"Article Data:\n{article_data}\n\n"
            f"Feature Extraction Template:\n{prompt_template}\n\n"
            "Respond in valid JSON:\n"
            '{"features": [str], "confidence": float}\n'
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
                else {"features": [], "confidence": 0.0}
            )
            features = result.get("features", [])
            confidence = result.get("confidence", 0.0)
        except Exception:
            features, confidence = [], 0.0
        return features, confidence
