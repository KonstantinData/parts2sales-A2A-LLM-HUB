"""
industry_class_agent.py

Purpose : Classifies industry category from features/descriptions using a dedicated scoring matrix.
Version : 1.1.2
Author  : Konstantin & AI Copilot
Notes   :
- Uses ScoringMatrixType.INDUSTRY for scoring and validation.
- Logs all events exclusively to logs/weighted_score/
- LLM usage and sample_data support (template-phase)
"""

from typing import Optional, Any, Dict
from datetime import datetime
from utils.schema import AgentEvent
from utils.scoring_matrix_types import ScoringMatrixType
from utils.scoring_matrix_loader import load_scoring_matrix
from utils.event_logger import write_event_log
from pathlib import Path

LOG_DIR = Path("logs") / "weighted_score"


class IndustryClassAgent:
    def __init__(
        self,
        scoring_matrix_type: ScoringMatrixType,
        threshold: float = 0.9,
        openai_client: Optional[Any] = None,
    ):
        self.agent_name = "IndustryClassAgent"
        self.agent_version = "1.1.2"
        self.scoring_matrix_type = scoring_matrix_type
        self.threshold = threshold
        self.openai_client = openai_client
        self.scoring_matrix = load_scoring_matrix(self.scoring_matrix_type)

    def run(
        self,
        input_text: str,
        base_name: str,
        iteration: int,
        prompt_version: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> AgentEvent:
        sample_data = (
            meta.get("sample_data") if meta and "sample_data" in meta else None
        )
        result = self.classify_industry(input_text, sample_data)
        event = AgentEvent(
            event_type="industry_class",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=result,
        )
        write_event_log(LOG_DIR, event)
        return event

    def classify_industry(self, input_text: str, sample_data=None) -> dict:
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized.")
        system_prompt = (
            "You are a B2B sector expert. Classify the industry of the described company/product. "
            "Use the scoring matrix below for quality. "
            'Output JSON: {"industry": <string>, "score": <float>, "feedback": <string>}'
        )
        matrix_desc = "\n".join(
            f"- {k}: weight {v}" for k, v in self.scoring_matrix.items()
        )
        user_prompt = (
            f"Input text:\n'''\n{input_text}\n'''\n\n"
            f"Scoring matrix:\n{matrix_desc}\n"
        )
        if sample_data:
            user_prompt += f"\nSample Data for validation:\n{sample_data}\n"
        user_prompt += "\nClassify the industry, give an overall score (0.0-1.0), and feedback. Output JSON as specified."
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=512,
            temperature=0.0,
        )
        import json

        try:
            content = response.choices[0].message.content
            result_json = json.loads(content)
            industry = result_json.get("industry", "")
            score = float(result_json.get("score", 0.0))
            feedback = result_json.get("feedback", "")
        except Exception as e:
            industry = ""
            score = 0.0
            feedback = f"LLM industry classification failed: {e}"
        return {
            "industry": industry,
            "score": score,
            "scoring_matrix": self.scoring_matrix,
            "feedback": feedback,
        }


__all__ = ["IndustryClassAgent"]
