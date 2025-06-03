"""
industry_class_agent.py

Purpose : Classifies industry relevance of a product prompt using scoring matrix and LLM.
Version : 1.1.1
Author  : Konstantin & AI Copilot
Notes   :
- Uses ScoringMatrixType.INDUSTRY for scoring.
- Returns detailed industry classification list.
- Fixes validation error by ensuring industry_classes is List[str].
"""

from typing import Optional, Any, Dict, List
from datetime import datetime
from utils.schema import AgentEvent, IndustryClassResult
from utils.scoring_matrix_types import ScoringMatrixType
from utils.scoring_matrix_loader import load_scoring_matrix


class IndustryClassAgent:
    def __init__(
        self,
        scoring_matrix_type: ScoringMatrixType = ScoringMatrixType.INDUSTRY,
        threshold: float = 0.9,
        openai_client: Optional[Any] = None,
    ):
        self.agent_name = "IndustryClassAgent"
        self.agent_version = "1.1.1"
        self.scoring_matrix_type = scoring_matrix_type
        self.threshold = threshold
        self.openai_client = openai_client
        self.scoring_matrix = load_scoring_matrix(self.scoring_matrix_type)

    def run(
        self,
        prompt_text: str,
        base_name: str,
        iteration: int,
        prompt_version: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> AgentEvent:
        result = self.classify_industries(prompt_text)
        event = AgentEvent(
            event_type="industry_class",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=result.dict(),
        )
        return event

    def classify_industries(self, prompt_text: str) -> IndustryClassResult:
        if self.openai_client is None:
            score = 1.0
            feedback = "No OpenAI client; dummy pass."
            pass_threshold = True
            industry_classes: List[str] = []
        else:
            scoring_prompt = (
                "Evaluate the prompt's industry classification quality based on these criteria:\n"
                + "\n".join(
                    f"- {k}: weight {v}" for k, v in self.scoring_matrix.items()
                )
                + f"\n\nPrompt:\n{prompt_text}\n\nReturn JSON with score (0-1), feedback (string), industry_classes (list of strings)."
            )
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an industry classification evaluator.",
                    },
                    {"role": "user", "content": scoring_prompt},
                ],
                temperature=0.3,
                max_tokens=400,
            )
            import json

            try:
                content = response.choices[0].message.content.strip()
                parsed = json.loads(content)
                score = float(parsed.get("score", 0))
                raw_feedback = parsed.get("feedback", "")
                if isinstance(raw_feedback, dict):
                    import json as js

                    feedback = js.dumps(raw_feedback)
                else:
                    feedback = str(raw_feedback)
                industry_classes_raw = parsed.get("industry_classes")
                if industry_classes_raw is None:
                    industry_classes = []
                elif isinstance(industry_classes_raw, list):
                    # Ensure list of strings (flatten dicts or other types)
                    industry_classes = []
                    for item in industry_classes_raw:
                        if isinstance(item, str):
                            industry_classes.append(item)
                        elif isinstance(item, dict):
                            # Flatten dict keys or values into strings (join keys for simplicity)
                            industry_classes.append(", ".join(item.keys()))
                        else:
                            industry_classes.append(str(item))
                else:
                    industry_classes = []
                pass_threshold = score >= self.threshold
            except Exception:
                score = 0.5
                feedback = "Failed to parse LLM industry classification output."
                industry_classes = []
                pass_threshold = False
        return IndustryClassResult(
            score=score,
            matrix=self.scoring_matrix,
            feedback=feedback,
            pass_threshold=pass_threshold,
            industry_classes=industry_classes,
            prompt_version=None,
        )
