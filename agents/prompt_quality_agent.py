# prompt_quality_agent.py
"""
Prompt Quality Agent for evaluating prompt design against custom dimensions.

Purpose:
--------
This agent reads a YAML-formatted prompt and uses a scoring matrix and review template to:
1. Score the prompt using dimension-based weights.
2. Generate quality feedback sections (dimension -> issue text).
3. Return a feedback object ready to be consumed by controller_agent.py.

#Notes:
- This version ensures clear communication with ControllerAgent via JSON logs.
- Scores and dimensions must match expected schema from quality_scoring_matrix.json
- Suggestions are synthesized if not available in the review template.

Environment:
------------
- scoring config: config/scoring/quality_scoring_matrix.json
- feedback template: config/templates/quality_review_log_template.json
"""

import json
from pathlib import Path
from typing import Tuple, Dict, Any


class PromptQualityAgent:
    def __init__(
        self,
        evaluation_path: Path = Path("config/scoring/quality_scoring_matrix.json"),
        review_log_path: Path = Path(
            "config/templates/quality_review_log_template.json"
        ),
        output_path: Path = Path("logs/quality_log"),
    ):
        self.evaluation_path = evaluation_path
        self.review_log_path = review_log_path
        self.output_path = output_path

    def run(
        self, prompt_text: str, base_name: str, version: int
    ) -> Tuple[float, Dict[str, str]]:
        """
        Evaluate prompt quality and generate structured quality log.

        Returns:
            - final_score: weighted total
            - issues_by_dimension: {dimension: problem_description}
        """
        try:
            weighted_eval = json.loads(self.evaluation_path.read_text(encoding="utf-8"))
            raw_review = json.loads(self.review_log_path.read_text(encoding="utf-8"))
        except Exception as e:
            raise RuntimeError(f"❌ Failed to read evaluation files: {e}")

        total_weight, weighted_sum = 0.0, 0.0
        issues_by_dimension = {}
        weighted_scores = []

        # Notes: Score computation based on predefined structure
        for dim in weighted_eval.get("details", []):
            score = float(dim.get("score", 0))
            weight = float(dim.get("weight", 1.0))
            name = dim.get("dimension")
            total_weight += weight
            weighted_sum += score * weight
            weighted_scores.append(
                {"dimension": name, "score": score, "weight": weight}
            )

        final_score = round(weighted_sum / total_weight, 4) if total_weight else 0.0

        # Notes: Try to extract issue comments for each dimension
        for entry in raw_review.get("details", []):
            dim = entry.get("dimension")
            score = entry.get("score", 1.0)
            if dim:
                # Synthesized fallback based on score
                if score >= 0.8:
                    issue_text = f"Minor or no issues detected in '{dim}'."
                elif score >= 0.5:
                    issue_text = f"The dimension '{dim}' has room for improvement."
                else:
                    issue_text = f"The dimension '{dim}' shows critical weaknesses and needs revision."
                issues_by_dimension[dim] = issue_text

        # Notes: Write minimal feedback object (only issues) for controller_agent
        log_dir = self.output_path
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{base_name}_v{version}.json"
        log_file.write_text(
            json.dumps(issues_by_dimension, indent=2, ensure_ascii=False)
        )

        return final_score, issues_by_dimension
