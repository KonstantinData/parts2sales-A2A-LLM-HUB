"""
company_match_agent.py

Purpose : Identifiziert und matched Firmen aus strukturierten oder unstrukturierten Daten (z.B. CRM, Anfrage, externen Datenquellen).
Version : 0.1.0-raw
Author  : Konstantin & AI Copilot
Notes   :
- Nutzt OpenAI LLM für intelligente, fehlertolerante Firmenzuordnung.
- Optional: Nachladen oder Scoring anhand von Datenbank/Listen möglich.
- Gibt ein AgentEvent zurück, das das Match-Ergebnis und relevante Metadaten enthält.

Example:
    agent = CompanyMatchAgent(openai_client=client)
    result = agent.run(prompt_text, meta={...})
"""

from typing import Dict, Any
from openai import OpenAI
from agents.utils.schemas import AgentEvent
from datetime import datetime


class CompanyMatchAgent:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.agent_name = "CompanyMatchAgent"
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
                "You are a matching expert. Identify and standardize company names or unique firm identifiers "
                "from the provided text. If ambiguity exists, return the most likely match and a confidence score (0-1)."
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

            payload = {
                "matched_company": llm_reply,
            }

            return AgentEvent(
                event_type="company_match",
                agent_name=self.agent_name,
                agent_version=self.agent_version,
                timestamp=datetime.utcnow(),
                step_id=step_id or "company_match",
                prompt_version=prompt_version,
                meta=meta or {},
                payload=payload,
            )
        except Exception as e:
            return AgentEvent(
                event_type="company_match",
                agent_name=self.agent_name,
                agent_version=self.agent_version,
                timestamp=datetime.utcnow(),
                step_id=step_id or "company_match",
                prompt_version=prompt_version,
                meta=meta or {},
                payload={
                    "status": "failed",
                    "error": str(e),
                },
            )
