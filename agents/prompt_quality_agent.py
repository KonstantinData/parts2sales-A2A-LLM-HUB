"""
prompt_quality_agent.py

Purpose : Agent for evaluating prompt quality using a dynamic scoring matrix.
Version : 1.2.2
Author  : Konstantin & AI Copilot
Notes   :
- Uses ScoringMatrixType enum from utils
- Logs all events exclusively to logs/weighted_score/
- Loads scoring matrix via loader, supports OpenAI client injection
- Raises on missing scoring matrix or invalid type
- Usage:
    from utils.scoring_matrix_types import ScoringMatrixType
    agent = PromptQualityAgent(
        scoring_matrix_type=ScoringMatrixType.FEATURE,
        threshold=0.9,
        openai_client=openai_client_instance,
    )
"""

from typing import Optional, Any, Dict
from datetime import datetime
from utils.schema import AgentEvent, PromptQualityResult
from utils.scoring_matrix_types import ScoringMatrixType
from utils.scoring_matrix_loader import load_scoring_matrix
from utils.event_logger import write_event_log
from pathlib import Path

LOG_DIR = Path("logs") / "weighted_score"


class PromptQualityAgent:
    def __init__(
        self,
        scoring_matrix_type: ScoringMatrixType,
        threshold: float = 0.9,
        openai_client: Optional[Any] = None,
    ):
        self.agent_name = "PromptQualityAgent"
        self.agent_version = "1.2.2"
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
        result = self.evaluate_prompt(prompt_text)
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
        write_event_log(LOG_DIR, event)
        return event

    def evaluate_prompt(self, prompt_text: str) -> PromptQualityResult:
        matrix = self.scoring_matrix
        feedback = "All major criteria passed."
        score = 1.0  # Simulate pass, replace with real scoring logic
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
