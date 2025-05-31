"""
PromptQualityAgent

This agent evaluates the quality of prompt templates based on predefined scoring dimensions.
It is designed to work in prompt development workflows where prompt quality is iteratively assessed
before prompt execution (e.g., via LLMs). The scoring is based on a weighted evaluation matrix
that defines relevant prompt-intrinsic dimensions.

Notes:
------
- The scoring matrix is defined in `template_scoring_matrix.py` and should reflect prompt-level criteria only.
- For evaluating LLM-generated outputs (e.g. search results), use a separate `example_scoring_matrix.py`.
- The agent expects the LLM response to be a strictly valid JSON array with `dimension`, `score`, and `comment` fields.
"""

import json
from pathlib import Path
from openai import OpenAI
from config.scoring.template_scoring_matrix import TEMPLATE_SCORING_MATRIX


class PromptQualityAgent:
    def __init__(
        self,
        client: OpenAI,
        evaluation_path: Path = Path("config/scoring/template_scoring_matrix.py"),
        creative_scoring: bool = False,
    ):
        self.client = client
        self.creative_scoring = creative_scoring
        self.evaluation_path = evaluation_path
        self.scoring_matrix = self._load_scoring_matrix()

    def _load_scoring_matrix(self):
        return TEMPLATE_SCORING_MATRIX

    def run(self, prompt_text: str, base_name: str, version: int):
        system_prompt = (
            "You are a prompt evaluation expert. "
            "Evaluate the given prompt on the following dimensions with scores between 0 and 1, "
            "and provide concrete suggestions for improvement. "
            "Return a strictly valid JSON array. No extra text."
        )
        user_prompt = f"Evaluate this prompt:\n\n{prompt_text}\n\nReturn JSON array."

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=700,
                )
                raw_output = response.choices[0].message.content.strip()
                feedback = json.loads(raw_output)
                break
            except json.JSONDecodeError as e:
                if attempt == 2:
                    raise e
                system_prompt = "Previous output was invalid JSON. Please ONLY return valid JSON array."

        weighted_sum = 0.0
        total_weight = 0.0
        for item in feedback:
            dim = item.get("dimension")
            score = item.get("score", 0.0)
            weight = self.scoring_matrix.get(dim, 1.0)
            weighted_sum += score * weight
            total_weight += weight

        weighted_score = weighted_sum / total_weight if total_weight else 0.0

        summary = {
            "prompt_score_weighted": weighted_score,
            "details": feedback,
        }

        return weighted_score, summary
