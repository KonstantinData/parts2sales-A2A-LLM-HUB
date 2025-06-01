"""
PromptQualityAgent evaluates the quality of prompts using either a scoring matrix, an LLM, or both.

#Notes:
- Uses the pydantic PromptQualityResult for structured output.
- All configs (scoring weights, rules, matrix version) are loaded from config/scoring/quality_scoring_matrix.json.
- Designed for traceability, audit, and easy upgrades.
- Uses Python logging for stepwise info and error reporting.
"""

import json
import logging
from typing import Dict, Optional
from agents.utils.schemas import PromptQualityResult, AgentEvent

# Setup logger for this agent
logger = logging.getLogger("PromptQualityAgent")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s"))
    logger.addHandler(handler)


class PromptQualityAgent:
    AGENT_NAME = "PromptQualityAgent"
    AGENT_VERSION = "1.1.0"  # Update this with each logic change

    def __init__(
        self, scoring_matrix_path="config/scoring/quality_scoring_matrix.json"
    ):
        self.scoring_matrix, self.matrix_version = self.load_matrix(scoring_matrix_path)
        logger.info(
            f"[{self.AGENT_NAME}] Loaded scoring matrix (version: {self.matrix_version})"
        )

    def load_matrix(self, path: str) -> (Dict, str):
        with open(path, encoding="utf-8") as f:
            matrix = json.load(f)
        version = matrix.get("version", "1.0")
        return matrix, version

    def matrix_score(self, prompt_text: str) -> PromptQualityResult:
        """
        Evaluates prompt using matrix rules.
        #Notes:
        - Replace the dummy scoring logic with more sophisticated checks as needed.
        """
        # Dummy logic: adjust per your rules/criteria!
        structure = 1.0 if "{" in prompt_text and "}" in prompt_text else 0.7
        clarity = 1.0 if "clear" in prompt_text.lower() else 0.8
        brevity = 1.0 if len(prompt_text) < 500 else 0.7
        tone = 1.0 if "please" not in prompt_text.lower() else 0.8

        weights = self.scoring_matrix.get(
            "weights", {"structure": 0.4, "clarity": 0.3, "brevity": 0.2, "tone": 0.1}
        )
        total = (
            weights["structure"] * structure
            + weights["clarity"] * clarity
            + weights["brevity"] * brevity
            + weights["tone"] * tone
        )
        logger.info(f"[{self.AGENT_NAME}] Matrix score: {total:.3f}")
        return PromptQualityResult(
            prompt=prompt_text,
            structure=structure,
            clarity=clarity,
            brevity=brevity,
            tone=tone,
            total=round(total, 3),
            method="matrix",
            scoring_matrix_version=self.matrix_version,
            prompt_length=len(prompt_text),
        )

    def llm_score(self, prompt_text: str) -> PromptQualityResult:
        """
        Uses an LLM to evaluate the prompt (dummy for now, can be integrated with OpenAI API).
        #Notes:
        - You can plug in OpenAI's GPT API and parse JSON to fill this result.
        """
        # Simulate LLM result
        logger.info(f"[{self.AGENT_NAME}] LLM score: 0.92")
        return PromptQualityResult(
            prompt=prompt_text,
            structure=0.9,
            clarity=0.9,
            brevity=0.95,
            tone=0.92,
            total=0.92,
            method="llm",
            scoring_matrix_version=self.matrix_version,
            prompt_length=len(prompt_text),
        )

    def score_prompt(
        self, prompt_text: str, method: str = "matrix"
    ) -> PromptQualityResult:
        """
        Main interface for the controller. Returns a PromptQualityResult.
        #Notes:
        - method: "matrix", "llm", or "hybrid".
        """
        if method == "matrix":
            return self.matrix_score(prompt_text)
        elif method == "llm":
            return self.llm_score(prompt_text)
        elif method == "hybrid":
            m = self.matrix_score(prompt_text)
            l = self.llm_score(prompt_text)
            # Average the scores
            return PromptQualityResult(
                prompt=prompt_text,
                structure=round((m.structure + l.structure) / 2, 3),
                clarity=round((m.clarity + l.clarity) / 2, 3),
                brevity=round((m.brevity + l.brevity) / 2, 3),
                tone=round((m.tone + l.tone) / 2, 3),
                total=round((m.total + l.total) / 2, 3),
                method="hybrid",
                scoring_matrix_version=self.matrix_version,
                prompt_length=len(prompt_text),
            )
        else:
            logger.error(f"Unknown scoring method: {method}")
            raise ValueError(f"Unknown scoring method: {method}")

    def score_event(
        self, prompt_text: str, method: str = "matrix", meta: Optional[dict] = None
    ) -> AgentEvent:
        """
        Returns a standardized AgentEvent for controller or logging.
        """
        result = self.score_prompt(prompt_text, method)
        event = AgentEvent(
            agent_name=self.AGENT_NAME,
            agent_version=self.AGENT_VERSION,
            event_type="prompt_quality_scored",
            event_payload=result.dict(),
            meta=meta,
        )
        logger.info(
            f"[{self.AGENT_NAME}] Event created: {event.event_type}, Score: {result.total}"
        )
        return event


# Usage example
if __name__ == "__main__":
    agent = PromptQualityAgent()
    example_prompt = "Fill out: {title}, {description}. Be clear and concise."
    event = agent.score_event(example_prompt, method="matrix")
    print(event.json(indent=2))
