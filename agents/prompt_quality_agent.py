"""
prompt_quality_agent.py

Purpose : Evaluates prompt quality using scoring matrix logic; returns detailed, type-safe AgentEvent.
Version : 1.2.0
Author  : Konstantin & AI Copilot
Notes   :
- Uses ScoringMatrixType Enum for full type safety and loader compatibility.
- Loads and applies the correct scoring matrix based on scoring_matrix_type.
- Provides structured score, feedback, and pass/fail threshold in the payload.
- No business logic change outside the required refactor for type safety.
- Supports extension for new scoring types by updating ScoringMatrixType.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from utils.scoring_matrix_types import ScoringMatrixType
from utils.schema import AgentEvent, PromptQualityResult
from utils.scoring_matrix_loader import (
    load_scoring_matrix,
)  # Helper to load scoring matrix by type


class PromptQualityAgent:
    def __init__(
        self,
        scoring_matrix_type: ScoringMatrixType,
        threshold: float = 0.9,
        openai_client: Optional[Any] = None,
    ):
        self.agent_name = "PromptQualityAgent"
        self.agent_version = "1.2.0"
        self.scoring_matrix_type = scoring_matrix_type
        self.threshold = threshold
        self.openai_client = openai_client
        self.scoring_matrix = load_scoring_matrix(self.scoring_matrix_type)

    def run(
        self,
        prompt_text: str,
        base_name: str,
        iteration: int,
        prompt_version: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> AgentEvent:
        # 1. Score prompt using loaded matrix (here: dummy logic, replace with real eval)
        result = self.evaluate_prompt(prompt_text)

        # 2. Package all output into the unified schema
        event = AgentEvent(
            event_type="prompt_quality",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=result.dict(),
        )
        return event

    def evaluate_prompt(self, prompt_text: str) -> PromptQualityResult:
        # TODO: Replace dummy with actual evaluation using OpenAI/scoring_matrix
        # Dummy: always pass with all features
        matrix = self.scoring_matrix
        feedback = "All major criteria passed."
        score = 1.0  # Simulate pass
        pass_threshold = score >= self.threshold
        issues = []
        return PromptQualityResult(
            score=score,
            matrix=matrix,
            feedback=feedback,
            pass_threshold=pass_threshold,
            issues=issues,
            prompt_version=None,
        )
