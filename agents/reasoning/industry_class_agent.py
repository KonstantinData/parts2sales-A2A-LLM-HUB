"""
industry_class_agent.py

Purpose : Classifies the relevant industry sector(s) for a product or text input using LLM.
Version : 0.1.0-raw
Author  : Konstantin & AI Copilot
Notes   :
- Uses OpenAI LLM for NAICS/NACE/ISIC or custom industry mapping.
- Returns a structured AgentEvent with detected industry codes/names and confidence scores.
- Handles errors gracefully with clear status in payload.

Example:
    agent = IndustryClassAgent(openai_client=client)
    result = agent.run(prompt_text, meta={...})
"""

from typing import Dict, Any
from openai import OpenAI
from agents.utils.schemas import AgentEvent
from datetime import datetime


class IndustryClassAgent:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.agent_name = "IndustryClassAgent"
        self.agent_version = "0.1.0-raw"

    def run(
        self,
        prompt_text: str,
        meta: Dict[str, Any] = None,
        prompt_version: str = None,
        step_id: str = None,
    ) -> AgentEvent:
        try:
            system_prompt = (
                "You are an industry classification expert. Given a product or company description, "
                "identify the most relevant industry (preferably by NACE/ISIC/NAICS code if possible) and return both the code and label. "
                "If multiple industries are plausible, return a ranked list."
            )

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_text},
                ],
                temperature=0.2,
            )

            llm_reply = response.choices[0].message.content.strip()

            # Optional: simple parser, can be replaced with stricter extraction
            industries = [
                line.strip("-• \n") for line in llm_reply.splitlines() if line.strip()
            ]
            industries = [i for i in industries if i]

            payload = {"industry_classes": industries, "raw_llm_reply": llm_reply}

            return AgentEvent(
                event_type="industry_classification",
                agent_name=self.agent_name,
                agent_version=self.agent_version,
                timestamp=datetime.utcnow(),
                step_id=step_id or "industry_classification",
                prompt_version=prompt_version,
                meta=meta or {},
                payload=payload,
            )
        except Exception as e:
            return AgentEvent(
                event_type="industry_classification",
                agent_name=self.agent_name,
                agent_version=self.agent_version,
                timestamp=datetime.utcnow(),
                step_id=step_id or "industry_classification",
                prompt_version=prompt_version,
                meta=meta or {},
                payload={
                    "status": "failed",
                    "error": str(e),
                },
            )
