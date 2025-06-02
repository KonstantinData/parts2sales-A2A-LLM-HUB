"""
agents/prompt_quality_agent.py

Evaluates prompt templates quality with process-specific scoring matrices.
Returns structured AgentEvent with PromptQualityResult payload.

# Notes:
- Dynamically loads scoring matrix by scoring_matrix_name.
- Supports Python or JSON matrix files.
- Prepared for LLM integration or rule-based scoring.
"""

import json
from pathlib import Path
from typing import Any, Dict
from agents.utils.schemas import AgentEvent, PromptQualityResult


class PromptQualityAgent:
    def __init__(
        self,
        openai_client,
        scoring_matrix_name: str = "template",
        agent_name="PromptQualityAgent",
        agent_version="1.0",
        scoring_dir: Path = None,
    ):
        self.openai = openai_client
        self.agent_name = agent_name
        self.agent_version = agent_version
        if scoring_dir is None:
            ROOT = Path(__file__).resolve().parent.parent
            scoring_dir = ROOT / "config" / "scoring"
        self.scoring_dir = scoring_dir
        self.scoring_matrix_name = scoring_matrix_name
        self.scoring_matrix = self._load_scoring_matrix(scoring_matrix_name)

    def _load_scoring_matrix(self, matrix_name: str) -> Dict[str, Any]:
        py_path = self.scoring_dir / f"{matrix_name}_scoring_matrix.py"
        json_path = self.scoring_dir / f"{matrix_name}_scoring_matrix.json"

        if py_path.exists():
            import importlib.util

            spec = importlib.util.spec_from_file_location("matrix", py_path)
            matrix = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(matrix)
            attr_name = f"{matrix_name.upper()}_SCORING_MATRIX"
            if hasattr(matrix, attr_name):
                return getattr(matrix, attr_name)
            else:
                raise AttributeError(f"Module {py_path} missing {attr_name}")
        elif json_path.exists():
            return json.loads(json_path.read_text(encoding="utf-8"))
        else:
            raise FileNotFoundError(
                f"Scoring matrix for '{matrix_name}' not found at {py_path} or {json_path}"
            )

    def run(
        self,
        prompt_text: str,
        base_name: str,
        iteration: int,
        prompt_version: str = None,
        meta: dict = None,
        method: str = "matrix",
    ) -> AgentEvent:
        meta = meta or {}
        score, matrix, feedback, issues = self._score_prompt(prompt_text)
        pass_threshold = score >= 0.9

        result = PromptQualityResult(
            score=score,
            matrix=matrix,
            feedback=feedback,
            pass_threshold=pass_threshold,
            issues=issues,
            prompt_version=prompt_version,
        )

        event = AgentEvent(
            event_type="prompt_quality",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            step_id=f"{base_name}_iter{iteration}",
            prompt_version=prompt_version,
            meta=meta,
            payload=result.dict(),
        )
        return event

    def _score_prompt(self, prompt_text: str):
        # Placeholder scoring: all criteria met = 1.0, extend for real scoring
        matrix = {key: 1.0 for key in self.scoring_matrix.keys()}
        score = sum(matrix.values()) / len(matrix) if matrix else 0.0
        feedback = (
            "Prompt meets all quality criteria."
            if score >= 0.9
            else "Prompt needs improvement."
        )
        issues = [] if score >= 0.9 else ["Structure issue", "Clarity issue"]
        return score, matrix, feedback, issues
