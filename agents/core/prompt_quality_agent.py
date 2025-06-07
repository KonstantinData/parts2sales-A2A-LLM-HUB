"""Prompt Quality Agent:
- Bewertet Prompts anhand einer Score-Matrix aus der Config.
- Nutzt LLM oder regelbasierte Scoring-Matrix.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ScoreResult:
    """Simple container for a prompt score."""
    total: float
    method: str


class PromptQualityAgent:
    """Lightweight prompt quality scorer used in unit tests."""

    def __init__(self, scoring_matrix_path: str | None = None) -> None:
        self.scoring_matrix_path = scoring_matrix_path

    def load_matrix(self) -> dict:
        if not self.scoring_matrix_path:
            return {}
        import json

        with open(self.scoring_matrix_path, encoding="utf-8") as f:
            return json.load(f)

    def _matrix_score(self, prompt_text: str) -> float:
        """Return a deterministic score based on placeholder usage."""
        placeholders = prompt_text.count("{")
        return min(1.0, placeholders / 3)

    def _llm_score(self, prompt_text: str) -> float:
        """Return a dummy LLM-based score.

        In the test environment we do not call an actual LLM, so this
        implementation derives a pseudo score from the prompt length.
        """
        return min(1.0, max(0.0, len(prompt_text) / 100))

    def score_prompt(self, prompt_text: str, method: str = "matrix") -> ScoreResult:
        """Score ``prompt_text`` using the specified method.

        Parameters
        ----------
        prompt_text:
            Text of the prompt to evaluate.
        method:
            ``"matrix"`` (default), ``"llm"`` or ``"hybrid"``.
        """
        method = method.lower()
        if method not in {"matrix", "llm", "hybrid"}:
            raise ValueError(f"Unknown scoring method: {method}")

        matrix_score = self._matrix_score(prompt_text)
        llm_score = self._llm_score(prompt_text)

        if method == "matrix":
            total = matrix_score
        elif method == "llm":
            total = llm_score
        else:  # hybrid
            total = (matrix_score + llm_score) / 2

        return ScoreResult(total=total, method=method)
