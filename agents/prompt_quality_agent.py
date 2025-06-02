"""
PromptQualityAgent

Purpose : Agent for realistic, rule-based quality assessment of prompts (RAW, TEMPLATE, domain layers).
Version : 1.2.0
Author  : Konstantin & AI Copilot
Notes   :
- Uses structured scoring matrix (configurable)
- Enforces minimum sections (objective, input_format, output_format)
- Expandable: structure, grammar, completeness, relevance (see TODO)
- Returns AgentEvent (Pydantic) with score, pass/fail, feedback, and issues
"""

from typing import Any, Dict, List, Optional
from utils.schema import AgentEvent  # Pfad anpassen, falls nötig


class PromptQualityAgent:
    def __init__(self, openai_client=None, scoring_matrix_name: str = "raw"):
        self.client = openai_client
        self.scoring_matrix_name = scoring_matrix_name

    def run(
        self,
        prompt_text: str,
        base_name: str,
        iteration: int,
        prompt_version: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> AgentEvent:
        score, issues = self._score_prompt(prompt_text)
        passed = score >= 0.9
        feedback = "" if passed else "; ".join(issues)
        payload = {
            "score": score,
            "scoring_matrix": self.scoring_matrix_name,
            "feedback": feedback,
            "pass_threshold": passed,
            "issues": issues,
        }
        return AgentEvent(
            name="PromptQualityAgent",
            version="1.2.0",
            timestamp=None,
            step="quality_evaluation",
            prompt_version=prompt_version,
            status="pass" if passed else "fail",
            payload=payload,
            meta=meta or {},
        )

    def _score_prompt(self, prompt_text: str) -> (float, List[str]):
        score = 1.0
        issues = []

        # 1. Required Sections
        if "objective" not in prompt_text:
            score -= 0.2
            issues.append("Missing 'objective' section.")
        if "input_format" not in prompt_text:
            score -= 0.2
            issues.append("Missing 'input_format' section.")
        if "output_format" not in prompt_text:
            score -= 0.2
            issues.append("Missing 'output_format' section.")

        # 2. Structure & Formatting (simple YAML keys check)
        if not self._has_proper_structure(prompt_text):
            score -= 0.1
            issues.append("Improper section structure or missing YAML keys.")

        # 3. Language Quality (dummy, extend with NLP or LLM as needed)
        if not self._is_grammatically_correct(prompt_text):
            score -= 0.1
            issues.append("Potential grammar or clarity issues detected.")

        # 4. Completeness (dummy, extend with coverage checks as needed)
        if not self._is_comprehensive(prompt_text):
            score -= 0.1
            issues.append("Prompt lacks coverage of relevant aspects.")

        # 5. Relevance (dummy, extend with keyword/topic checks as needed)
        if not self._is_relevant(prompt_text):
            score -= 0.1
            issues.append("Prompt may contain irrelevant information.")

        score = max(score, 0.0)
        return score, issues

    def _has_proper_structure(self, text: str) -> bool:
        """Minimal YAML section check; can be replaced with real YAML loader."""
        must_have = ["role:", "objective:", "input_format:", "output_format:"]
        return all(k in text for k in must_have)

    def _is_grammatically_correct(self, text: str) -> bool:
        """Dummy: always returns True. Integrate NLP/LLM check for real implementation."""
        # TODO: Implement grammar check with LLM or rule-based method
        return True

    def _is_comprehensive(self, text: str) -> bool:
        """Dummy: always returns True. Extend for coverage of required fields or typical attributes."""
        # TODO: Implement check for all key aspects present (domain specific)
        return True

    def _is_relevant(self, text: str) -> bool:
        """Dummy: always returns True. Could scan for banned terms, off-topic content."""
        # TODO: Implement relevance check with heuristics or LLM
        return True
