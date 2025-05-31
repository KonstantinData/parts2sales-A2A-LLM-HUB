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
                # Optional: Log raw_output for debugging
                if attempt == 2:
                    raise e
                # Retry, modify system prompt to demand strictly valid JSON next time
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
