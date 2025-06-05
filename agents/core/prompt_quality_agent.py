"""Minimal prompt quality agent used only for unit tests."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ScoreResult:
    """Simple container for a prompt score."""

    total: float
    method: str


class PromptQualityAgent:
    """Return deterministic scores for different methods."""

    def __init__(self) -> None:
        # No state required; this agent merely returns hard coded values
        pass

    def score_prompt(self, prompt: str, method: str = "matrix") -> ScoreResult:
        """Return a pseudo score so that unit tests can run."""
        method = method.lower()
        if method == "matrix":
            score = 0.8
        elif method == "llm":
            score = 0.9
        elif method == "hybrid":
            score = 0.85
        else:
            raise ValueError("Unsupported method")

        # Wrap the chosen score in the simple dataclass
        return ScoreResult(total=score, method=method)
