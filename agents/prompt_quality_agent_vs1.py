import json
from pathlib import Path
from openai import OpenAI


class PromptQualityAgent:
    def __init__(
        self,
        client: OpenAI,
        evaluation_path: Path = Path("config/scoring/quality_scoring_matrix.json"),
        creative_scoring: bool = False,
    ):
        self.client = client
        self.creative_scoring = creative_scoring
        self.evaluation_path = evaluation_path
        self.scoring_matrix = self._load_scoring_matrix()

    def _load_scoring_matrix(self):
        try:
            with open(self.evaluation_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {
                dim["dimension"]: dim["weight"] for dim in data.get("dimensions", [])
            }
        except Exception as e:
            print(f"⚠️ Failed to load scoring matrix: {e}")
            return {}

    def run(self, prompt_text: str, base_name: str, version: int):
        dimensions_list = list(self.scoring_matrix.keys())
        dimensions_str = ", ".join(dimensions_list)

        system_prompt = (
            "You are a prompt evaluation expert. "
            f"Evaluate the given prompt on the following dimensions: {dimensions_str}. "
            "For each dimension, provide:\n"
            "- score: float between 0 (poor) and 1 (excellent)\n"
            "- positive: what is done well\n"
            "- suggestion: how to improve\n"
            "Return a JSON array with one object per dimension, e.g.:\n"
            '[{"dimension": "task_clarity", "score": 0.8, "positive": "...", "suggestion": "..."}, ...]\n'
            "Be honest and critical. Use a balanced tone.\n"
        )

        user_prompt = (
            f"Evaluate this prompt text:\n\n{prompt_text}\n\n"
            "Return only the JSON array as described above. No extra commentary."
        )

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

            # Save raw response for debugging
            debug_filename = f"debug_quality_response_{base_name}_v{version}.json"
            with open(debug_filename, "w", encoding="utf-8") as f:
                f.write(raw_output)

            feedback = json.loads(raw_output)

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

        except Exception as e:
            error_summary = {
                "error": str(e),
                "prompt_score_weighted": 0.0,
                "details": [],
            }
            return 0.0, error_summary
