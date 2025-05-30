#!/usr/bin/env python3
"""
File: prompt_quality_agent.py
Type: Python Module (Agent Class)

Purpose:
--------
This agent evaluates a YAML prompt against defined quality dimensions and produces a structured feedback log
for downstream agents to consume. It uses a weighted scoring system based on predefined evaluation criteria.

Returns a feedback dictionary containing:
- Weighted score (float)
- List of score components per dimension
- Suggestions for improvement
- Raw review log (source for improvement agent)
"""

import json
from pathlib import Path
from typing import Tuple


class PromptQualityAgent:
    def __init__(
        self,
        evaluation_path: Path = Path("config/scoring/quality_scoring_matrix.json"),
        review_log_path: Path = Path(
            "config/templates/quality_review_log_template.json"
        ),
    ):
        self.evaluation_path = evaluation_path
        self.review_log_path = review_log_path

    def run(self, prompt_text: str) -> Tuple[float, dict]:
        """
        Evaluate prompt and return score with feedback package.
        """
        # Notes: prompt_text is currently unused – will be needed for real-time eval later

        try:
            weighted_eval = json.loads(self.evaluation_path.read_text(encoding="utf-8"))
            raw_log = json.loads(self.review_log_path.read_text(encoding="utf-8"))
        except Exception as e:
            raise RuntimeError(f"Failed to read input files: {e}")

        # Notes: calculate total weighted score
        weighted_scores = []
        total_weight = 0.0
        weighted_sum = 0.0

        for dim in weighted_eval:
            score = dim["score"]
            weight = dim.get("weight", 1.0)
            weighted_sum += score * weight
            total_weight += weight
            weighted_scores.append(
                {"dimension": dim["dimension"], "score": score, "weight": weight}
            )

        final_score = round(weighted_sum / total_weight, 4) if total_weight else 0.0

        # Notes: compile suggestions from raw_log if present
        suggestions = []
        for entry in raw_log:
            dim = entry.get("dimension")
            advice = entry.get("suggestion") or entry.get("recommendation")
            if dim and advice:
                suggestions.append({"dimension": dim, "suggestion": advice})

        # Notes: consolidate final feedback object
        feedback = {
            "score": final_score,
            "score_components": weighted_scores,
            "suggestions": suggestions,
            "raw_review_log": raw_log,
        }

        return final_score, feedback
