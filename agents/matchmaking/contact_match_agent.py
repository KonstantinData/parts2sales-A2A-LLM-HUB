"""
contact_match_agent.py

Purpose : Matches and ranks contacts to companies.
Version : 1.1.0
Author  : Konstantin & AI Copilot
Notes   :
- Uses ScoringMatrixType.CONTACT for evaluation and ranking.
- Returns AgentEvent with traceable payload structure.
- Can be extended for CRM integration or LLM-based matching.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.scoring_matrix_types import ScoringMatrixType
from utils.schema import AgentEvent


class ContactMatchAgent:
    def __init__(
        self,
        scoring_matrix_type: ScoringMatrixType = ScoringMatrixType.CONTACT,
        openai_client: Optional[Any] = None,
    ):
        self.agent_name = "ContactMatchAgent"
        self.agent_version = "1.1.0"
        self.scoring_matrix_type = scoring_matrix_type
        self.openai_client = openai_client

    def run(
        self,
        input_data: Dict[str, Any],
        base_name: str,
        iteration: int,
        prompt_version: str = None,
        meta: Dict[str, Any] = None,
    ) -> AgentEvent:
        # Dummy logic for now – in production use CRM or LLM logic.
        contacts = self._match_contacts(input_data)
        payload = {
            "contacts": contacts,
            "input": input_data,
            "info": "Contact matching complete.",
        }
        event = AgentEvent(
            event_type="contact_matching",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )
        return event

    def _match_contacts(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Example result – production could use HubSpot or another DB.
        return [
            {"name": "Maria Schmidt", "role": "Purchasing Manager", "confidence": 0.81},
            {"name": "Peter Müller", "role": "Head of Engineering", "confidence": 0.73},
        ]
