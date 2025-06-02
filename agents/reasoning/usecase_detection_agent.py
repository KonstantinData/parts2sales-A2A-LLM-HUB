"""
usecase_detection_agent.py

Purpose : Erkennt und extrahiert relevante Use Cases aus Produkt-, Anfrage- oder Textdaten.
Version : 0.1.0-raw
Author  : Konstantin & AI Copilot

- Nutzt OpenAI LLM zur semantischen Analyse und Einordnung.
- Gibt AgentEvent mit den erkannten Use Cases, Zuverlässigkeit, und Metadaten zurück.
- Unterstützt individuelle Vorgaben/Listen per Meta-Argument.

Example:
    agent = UseCaseDetectionAgent(openai_client=client)
    result = agent.run(prompt_text, meta={...})
"""

from typing import Dict, Any, List
from openai import OpenAI
from agents.utils.schemas import AgentEvent
from datetime import datetime


class UseCaseDetectionAgent:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.agent_name = "UseCaseDetectionAgent"
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
                "You are an expert for industrial and commercial product use case detection. "
                "Extract a list of the most relevant use cases (between 2 and 7) from the following description. "
                "Only use information given in the text, no speculation."
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

            # Annahme: LLM gibt eine kommagetrennte oder Listenstruktur zurück.
            usecases = [
                uc.strip("-• \n") for uc in llm_reply.splitlines() if uc.strip()
            ]
            usecases = [uc for uc in usecases if uc]  # Leere raus

            payload = {"usecases": usecases, "raw_llm_reply": llm_reply}

            return AgentEvent(
                event_type="usecase_detection",
                agent_name=self.agent_name,
                agent_version=self.agent_version,
                timestamp=datetime.utcnow(),
                step_id=step_id or "usecase_detection",
                prompt_version=prompt_version,
                meta=meta or {},
                payload=payload,
            )
        except Exception as e:
            return AgentEvent(
                event_type="usecase_detection",
                agent_name=self.agent_name,
                agent_version=self.agent_version,
                timestamp=datetime.utcnow(),
                step_id=step_id or "usecase_detection",
                prompt_version=prompt_version,
                meta=meta or {},
                payload={
                    "status": "failed",
                    "error": str(e),
                },
            )
