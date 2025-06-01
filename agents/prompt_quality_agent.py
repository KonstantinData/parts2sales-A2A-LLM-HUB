"""
PromptQualityAgent

This agent evaluates the quality of prompt templates based on a scoring matrix (from config).
It works in agentic workflows, always returning structured AgentEvent with a PromptQualityResult payload.

Notes:
------
- Matrix is defined in config/scoring/template_scoring_matrix.json or .py.
- Uses OpenAI LLM if 'llm' mode is specified, or matrix rules otherwise.
- Always returns an AgentEvent (for logging, tracking, workflow chaining).
"""

import json
from typing import Any, Dict
from datetime import datetime
from agents.utils.schemas import AgentEvent, PromptQualityResult


class PromptQualityAgent:
    def __init__(
        self,
        openai_client,
        evaluation_path,
        agent_name="PromptQualityAgent",
        agent_version="1.0",
    ):
        self.openai = openai_client
        self.evaluation_path = evaluation_path
        self.agent_name = agent_name
        self.agent_version = agent_version
        # Optionally: Load scoring matrix at init
        self.scoring_matrix = self._load_scoring_matrix()

    def _load_scoring_matrix(self) -> Dict[str, Any]:
        if self.evaluation_path.suffix == ".json":
            return json.loads(self.evaluation_path.read_text(encoding="utf-8"))
        elif self.evaluation_path.suffix == ".py":
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "matrix", self.evaluation_path
            )
            matrix = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(matrix)
            return matrix.SCORING_MATRIX
        else:
            raise ValueError("Unsupported matrix file type.")

    def run(
        self,
        prompt_text: str,
        base_name: str,
        iteration: int,
        prompt_version: str = None,
        meta: dict = None,
        method: str = "matrix",
    ) -> AgentEvent:
        """
        Evaluate a prompt with the scoring matrix or LLM and return AgentEvent.
        """
        meta = meta or {}
        # Step 1: Calculate matrix score
        # Here, we just simulate a scoring. In practice, use your scoring logic or LLM call.
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
        # TODO: Replace this stub with your real scoring logic, possibly LLM call.
        # Example: All criteria found? Dummy output for now.
        matrix = {key: 1.0 for key in self.scoring_matrix.keys()}
        score = sum(matrix.values()) / len(matrix) if matrix else 0.0
        feedback = (
            "Prompt meets all quality criteria."
            if score >= 0.9
            else "Prompt needs improvement."
        )
        issues = [] if score >= 0.9 else ["Structure issue", "Clarity issue"]
        return score, matrix, feedback, issues
