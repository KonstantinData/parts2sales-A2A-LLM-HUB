"""Prompt Quality Agent used in unit tests.

This simplified agent now only generates a score via a pseudo LLM
implementation.  Any former matrix based scoring logic has been
removed so tests rely solely on the single LLM based scorer.
"""

from dataclasses import dataclass


@dataclass
class ScoreResult:
    """Simple container for a prompt score."""

    total: float
    method: str


class PromptQualityAgent:
    """Lightweight prompt quality scorer used in unit tests."""

    def __init__(self) -> None:  # pragma: no cover - simple container
        pass

    def _llm_score(self, prompt_text: str) -> float:
        """Return a dummy LLM-based score.

        In the test environment we do not call an actual LLM, so this
        implementation derives a pseudo score from the prompt length.
        """
        return min(1.0, max(0.0, len(prompt_text) / 100))

    def score_prompt(self, prompt_text: str) -> ScoreResult:
        """Score ``prompt_text`` using the pseudo LLM scorer."""

        total = self._llm_score(prompt_text)
        return ScoreResult(total=total, method="llm")
