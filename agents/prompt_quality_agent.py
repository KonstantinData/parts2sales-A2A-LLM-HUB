"""
PromptQualityAgent

Purpose : Agent for quality assessment of prompts in RAW, TEMPLATE and domain-specific layers.
Version : 1.1.0
Author  : Konstantin’s AI Copilot
Notes   :
- Imports all scoring matrices and selects by scoring_matrix_name (e.g., "raw", "template", ...)
- Returns AgentEvent (Pydantic) with scoring, threshold, and feedback
- Robust error handling, structured log-ready output
"""

import importlib
from typing import Dict, Any

from agents.utils.schemas import AgentEvent

SCORING_MATRICES = {
    "raw": "config.scoring.raw_scoring_matrix.RAW_SCORING_MATRIX",
    "template": "config.scoring.template_scoring_matrix.TEMPLATE_SCORING_MATRIX",
    "feature": "config.scoring.feature_scoring_matrix.FEATURE_SCORING_MATRIX",
    "usecase": "config.scoring.usecase_scoring_matrix.USECASE_SCORING_MATRIX",
    "industry": "config.scoring.industry_scoring_matrix.INDUSTRY_SCORING_MATRIX",
    "contact": "config.scoring.contact_scoring_matrix.CONTACT_SCORING_MATRIX",
    # Extend as needed
}


class PromptQualityAgent:
    def __init__(self, openai_client=None, scoring_matrix_name: str = "raw"):
        self.openai_client = openai_client
        self.scoring_matrix_name = scoring_matrix_name

        # Dynamically import the correct matrix
        if scoring_matrix_name not in SCORING_MATRICES:
            raise ValueError(f"Unknown scoring matrix: {scoring_matrix_name}")
        mod_path, var_name = SCORING_MATRICES[scoring_matrix_name].rsplit(".", 1)
        module = importlib.import_module(mod_path)
        self.scoring_matrix = getattr(module, var_name)

    def run(
        self,
        prompt_text: str,
        base_name: str,
        iteration: int,
        prompt_version: str,
        meta: Dict[str, Any],
    ) -> AgentEvent:
        score, issues = self._score_prompt(prompt_text)
        passed = score >= 0.9

        payload = {
            "score": score,
            "matrix": self.scoring_matrix,
            "feedback": "" if passed else f"Issues: {issues}",
            "pass_threshold": passed,
            "issues": issues,
        }

        return AgentEvent(
            name="PromptQualityAgent",
            version="1.1.0",
            timestamp=None,
            step="quality_evaluation",
            prompt_version=prompt_version,
            status="pass" if passed else "fail",
            payload=payload,
            meta=meta,
        )

    def _score_prompt(self, prompt_text: str):
        # Dummy: All criteria positive, but here plug in your scoring logic!
        issues = []
        score = 1.0
        for criterion in self.scoring_matrix:
            # Implement actual NLP or regex-based checks here for real QC!
            # If fails, append to issues.
            continue
        return score, issues
