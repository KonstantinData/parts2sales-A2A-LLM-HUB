"""
feature_extraction_agent.py

Purpose : Agent for extracting product features using a dedicated scoring matrix.
Version : 1.1.0
Author  : Konstantin & AI Copilot
Notes   :
- Uses ScoringMatrixType.FEATURE for scoring
- Performs feature extraction quality evaluation via LLM
- Emits structured AgentEvent with feature extraction results
"""

from typing import Optional, Any, Dict
from datetime import datetime
from utils.schema import AgentEvent, FeatureExtractionResult
from utils.scoring_matrix_types import ScoringMatrixType
from utils.scoring_matrix_loader import load_scoring_matrix


class FeatureExtractionAgent:
    def __init__(
        self,
        scoring_matrix_type: ScoringMatrixType = ScoringMatrixType.FEATURE,
        threshold: float = 0.9,
        openai_client: Optional[Any] = None,
    ):
        self.agent_name = "FeatureExtractionAgent"
        self.agent_version = "1.1.0"
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
        result = self.evaluate_features(prompt_text)
        event = AgentEvent(
            event_type="feature_extraction",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=result.dict(),
        )
        return event

    def evaluate_features(self, prompt_text: str) -> FeatureExtractionResult:
        if self.openai_client is None:
            # Dummy pass
            score = 1.0
            feedback = "No OpenAI client; dummy pass."
            pass_threshold = True
            extracted_features = []
        else:
            scoring_prompt = (
                "Evaluate the prompt's feature extraction quality based on these criteria:\n"
                + "\n".join(
                    f"- {k}: weight {v}" for k, v in self.scoring_matrix.items()
                )
                + f"\n\nPrompt:\n{prompt_text}\n\nReturn JSON with score (0-1), feedback, extracted_features."
            )
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product feature extraction evaluator.",
                    },
                    {"role": "user", "content": scoring_prompt},
                ],
                temperature=0.3,
                max_tokens=300,
            )
            import json

            try:
                content = response.choices[0].message.content.strip()
                parsed = json.loads(content)
                score = float(parsed.get("score", 0))
                feedback = parsed.get("feedback", "")
                extracted_features = parsed.get("extracted_features", [])
                pass_threshold = score >= self.threshold
            except Exception:
                score = 0.5
                feedback = "Failed to parse LLM feature extraction output."
                extracted_features = []
                pass_threshold = False
        return FeatureExtractionResult(
            score=score,
            matrix=self.scoring_matrix,
            feedback=feedback,
            pass_threshold=pass_threshold,
            extracted_features=extracted_features,
            prompt_version=None,
        )
