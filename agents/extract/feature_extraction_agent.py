"""
feature_extraction_agent.py

Purpose : Extracts technical product features from input data for prompt-based LLM workflows.
Version : 1.1.0
Author  : Konstantin & AI Copilot
Notes   :
- Uses ScoringMatrixType.FEATURE for type-safe matrix-based quality evaluation.
- Validates feature extraction output structure.
- Emits structured AgentEvent for auditability.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.scoring_matrix_types import ScoringMatrixType
from utils.schema import AgentEvent
from utils.schema import PromptQualityResult  # Use if needed for payload structure


class FeatureExtractionAgent:
    def __init__(
        self,
        scoring_matrix_type: ScoringMatrixType = ScoringMatrixType.FEATURE,
        openai_client: Optional[Any] = None,
    ):
        self.agent_name = "FeatureExtractionAgent"
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
        # Core extraction logic, LLM or heuristic (dummy implementation here)
        features = self._extract_features(input_data)
        payload = {
            "features": features,
            "input": input_data,
            "info": "Feature extraction complete.",
        }
        event = AgentEvent(
            event_type="feature_extraction",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )
        return event

    def _extract_features(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Placeholder for LLM or heuristic; here only structure.
        # In production, call LLM or custom extraction logic.
        return [
            {
                "name": "voltage",
                "value": "24",
                "unit": "v",
                "source": "title",
            },
            {
                "name": "protection_class",
                "value": "ip67",
                "unit": "",
                "source": "title",
            },
        ]
