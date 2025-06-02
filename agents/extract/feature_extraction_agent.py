"""
feature_extraction_agent.py

Purpose : Extracts structured product features from input prompt using LLM.
Version : 0.1.0-raw
Author  : Konstantin & AI Copilot
Notes   :
- Depends on OpenAI LLM client and prompt schemas.
- Error-handling: Returns AgentEvent with 'failed' status and error details on exception.
- Usage: Used by controller as a specialist agent for feature extraction.

Example:
    agent = FeatureExtractionAgent(openai_client=client)
    result = agent.run(prompt_text, meta={...})
"""

from typing import Dict, Any
from openai import OpenAI
from agents.utils.schemas import AgentEvent
from datetime import datetime


class FeatureExtractionAgent:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.agent_name = "FeatureExtractionAgent"
        self.agent_version = "0.1.0-raw"

    def run(
        self,
        prompt_text: str,
        meta: Dict[str, Any] = None,
        prompt_version: str = None,
        step_id: str = None,
    ) -> AgentEvent:
        try:
            # Example completion call; customize system/user prompt for your workflow
            system_prompt = (
                "You are an expert at extracting technical features from product descriptions. "
                "Extract only factual, measurable product attributes. "
                "Respond in strict JSON per the output_schema."
            )

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_text},
                ],
                temperature=0,
            )

            llm_reply = response.choices[0].message.content.strip()
            # Attempt to parse as JSON (optional, for further validation)

            payload = {
                "extracted_features": llm_reply,
            }

            return AgentEvent(
                event_type="feature_extraction",
                agent_name=self.agent_name,
                agent_version=self.agent_version,
                timestamp=datetime.utcnow(),
                step_id=step_id or "feature_extraction",
                prompt_version=prompt_version,
                meta=meta or {},
                payload=payload,
            )
        except Exception as e:
            return AgentEvent(
                event_type="feature_extraction",
                agent_name=self.agent_name,
                agent_version=self.agent_version,
                timestamp=datetime.utcnow(),
                step_id=step_id or "feature_extraction",
                prompt_version=prompt_version,
                meta=meta or {},
                payload={
                    "status": "failed",
                    "error": str(e),
                },
            )
