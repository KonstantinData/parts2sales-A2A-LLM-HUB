"""
contact_match_agent.py

Purpose : Matches and ranks contacts to companies based on contextual relevance, using LLM and/or scoring logic.
Version : 0.1.0-raw
Author  : Konstantin & AI Copilot
Notes   :
- Accepts contact and company lists or descriptors.
- Returns ranked list of contacts per company with confidence scores and rationales.
- Integrates scoring matrices from config/scoring/contact_scoring_matrix.py if available.
- Can be extended for batch or streaming evaluation.

Example:
    agent = ContactMatchAgent(openai_client=client)
    event = agent.run(
        contacts=[...],
        companies=[...],
        meta={...}
    )
"""

from typing import List, Dict, Any, Optional
from agents.utils.schemas import AgentEvent
from datetime import datetime
from openai import OpenAI

try:
    from config.scoring.contact_scoring_matrix import CONTACT_SCORING_MATRIX
except ImportError:
    CONTACT_SCORING_MATRIX = {}


class ContactMatchAgent:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.agent_name = "ContactMatchAgent"
        self.agent_version = "0.1.0-raw"

    def run(
        self,
        contacts: List[Dict[str, Any]],
        companies: List[Dict[str, Any]],
        meta: Optional[Dict[str, Any]] = None,
        prompt_version: Optional[str] = None,
        step_id: Optional[str] = None,
        scoring_matrix: Optional[Dict[str, Any]] = None,
        top_n: int = 3,
    ) -> AgentEvent:
        scoring_matrix = scoring_matrix or CONTACT_SCORING_MATRIX
        prompt_contacts = "\n".join(
            [
                f"{c['name']} ({c.get('email', '-')}, {c.get('role', '-')})"
                for c in contacts
            ]
        )
        prompt_companies = "\n".join(
            [f"{c['name']} ({c.get('industry', '-')})" for c in companies]
        )
        llm_prompt = (
            f"Given the following list of companies:\n{prompt_companies}\n"
            f"And these available contacts:\n{prompt_contacts}\n"
            "Match and rank the best contacts for each company based on their likely fit and context. "
            "Respond as a JSON object: {company: [ {name, reason, confidence_score (0-1.0)} ] }."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert contact-to-company matcher.",
                    },
                    {"role": "user", "content": llm_prompt},
                ],
                temperature=0.2,
            )
            llm_reply = response.choices[0].message.content.strip()
        except Exception as e:
            return AgentEvent(
                event_type="contact_matching",
                agent_name=self.agent_name,
                agent_version=self.agent_version,
                timestamp=datetime.utcnow(),
                step_id=step_id or "contact_matching",
                prompt_version=prompt_version,
                meta=meta or {},
                payload={"status": "failed", "error": str(e)},
            )

        try:
            import json

            result = json.loads(llm_reply)
        except Exception:
            result = {}
        payload = {
            "matches": result,
            "raw_llm_reply": llm_reply,
            "scoring_matrix_used": bool(scoring_matrix),
        }

        return AgentEvent(
            event_type="contact_matching",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=step_id or "contact_matching",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )
