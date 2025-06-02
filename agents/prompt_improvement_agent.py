"""
prompt_improvement_agent.py

Purpose : Improves prompt text based on feedback from the quality agent and current scoring matrix.
Version : 1.1.0
Author  : Konstantin & AI Copilot
Notes   :
- Uses ScoringMatrixType Enum for context (type-safe).
- Optionally, could use scoring matrix in the future for context-aware improvement (here als Platzhalter, falls gewünscht).
- Produces improved prompt and rationale as payload.
"""

from typing import Dict, Any
from datetime import datetime
from utils.scoring_matrix_types import ScoringMatrixType
from utils.schema import AgentEvent
from utils.schema import PromptQualityResult


class PromptImprovementAgent:
    def __init__(self, scoring_matrix_type: ScoringMatrixType = None):
        self.agent_name = "PromptImprovementAgent"
        self.agent_version = "1.1.0"
        self.scoring_matrix_type = scoring_matrix_type

    def run(
        self,
        prompt_text: str,
        feedback: str,
        base_name: str,
        iteration: int,
        prompt_version: str = None,
        meta: Dict[str, Any] = None,
    ) -> AgentEvent:
        # --- Hier später Matrix- oder Typ-Spezifik-Logik möglich ---
        improved_prompt, rationale = self.improve_prompt(prompt_text, feedback)
        payload = {
            "improved_prompt": improved_prompt,
            "rationale": rationale,
        }
        event = AgentEvent(
            event_type="prompt_improvement",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )
        return event

    def improve_prompt(self, prompt_text: str, feedback: str):
        # TODO: Replace dummy logic with a real LLM-based improvement step
        # Here, just a stub that appends feedback as a comment
        improved = prompt_text + "\n# FEEDBACK FOR IMPROVEMENT:\n" + feedback
        rationale = "Appended feedback as instruction for improvement."
        return improved, rationale
