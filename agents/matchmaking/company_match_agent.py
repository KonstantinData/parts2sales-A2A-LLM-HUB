"""
company_match_agent.py

Purpose : Matches and ranks companies based on product data, metadata, or context.
Version : 1.1.0
Author  : Konstantin & AI Copilot
Notes   :
- Uses ScoringMatrixType.COMPANY for scoring logic and evaluation.
- Emits unified AgentEvent for downstream traceability.
- Modular: can connect to any matching DB, LLM, or external service.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.scoring_matrix_types import ScoringMatrixType
from utils.schema import AgentEvent


class CompanyMatchAgent:
    def __init__(
        self,
        scoring_matrix_type: ScoringMatrixType = ScoringMatrixType.COMPANY,
        openai_client: Optional[Any] = None,
    ):
        self.agent_name = "CompanyMatchAgent"
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
        # Dummy logic: Replace with LLM, retrieval, or lookup as needed.
        companies = self._match_companies(input_data)
        payload = {
            "companies": companies,
            "input": input_data,
            "info": "Company matching complete.",
        }
        event = AgentEvent(
            event_type="company_matching",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )
        return event

    def _match_companies(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Example output; in production use retrieval, embeddings, or LLM.
        return [
            {"name": "Siemens AG", "confidence": 0.89},
            {"name": "Schneider Electric", "confidence": 0.77},
        ]
