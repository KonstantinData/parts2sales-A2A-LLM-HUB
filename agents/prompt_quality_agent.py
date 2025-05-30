#!/usr/bin/env python3
"""
File: prompt_quality_agent.py
Type: Python Module (Agent Implementation)

Purpose:
--------
This module implements the PromptQualityAgent, a rule-based agent that
analyzes YAML prompts for clarity, structure, tone, grammar, idiomatic usage,
and LLM-compatibility. It builds on top of a validation engine defined in
`validate_prompt_en` and outputs structured results.

Usage:
------
Used within the prompt validation workflow to compute a quality score and
detailed diagnostics before passing the prompt to improvement routines.

Notes:
------
- Requires `language_tool_python`, `lang_en.py` and `validate_prompt_en`.
- Outputs a structured dictionary with score and failed checks.
"""

from agents.base_agent import BaseAgent
from prompt_quality.validators.validate_prompt_quality_en import validate_prompt_en
from prompt_quality.languages import lang_en
from typing import Tuple
import json


class PromptQualityAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="PromptQualityAgent")

    def run(self, prompt_text: str) -> Tuple[float, dict]:
        """
        Run validation checks on the provided prompt string.

        Args:
            prompt_text (str): The YAML prompt content as a string.

        Returns:
            Tuple[float, dict]: Total score and detailed check results
        """
        results = validate_prompt_en(prompt_text)

        # Note: Scoring logic based on predefined weights
        weights = {
            "grammar_check": 0.10,
            "idiomatic_check": 0.05,
            "task_clarity": 0.30,
            "structure_check": 0.25,
            "lexical_fit": 0.10,
            "tone_check": 0.10,
            "translation_integrity": 0.10,
        }

        score = 0.0
        for check, weight in weights.items():
            if results.get(check, {}).get("passed", False):
                score += weight

        score = round(score * 20) / 20  # Note: Round to nearest 0.05 step

        return score, results
