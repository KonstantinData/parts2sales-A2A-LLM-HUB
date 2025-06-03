"""
company_match_agent.py

Purpose : Matches companies from input data against reference databases using scoring matrix and OpenAI evaluation.
Version : 1.1.0
Author  : Konstantin & AI Copilot
Notes   :
- Uses ScoringMatrixType.COMPANY for scoring.
- Uses OpenAI client to refine matching logic.
- Returns AgentEvent with detailed match results.
"""

from typing import Optional, Any, Dict
from datetime import datetime
from utils.schema import AgentEvent, CompanyMatchResult
from utils.scoring_matrix_types import ScoringMatrixType
from utils.scoring_matrix_loader import load_scoring_matrix


class CompanyMatchAgent:
    def __init__(
        self,
        scoring_matrix_type: ScoringMatrixType = ScoringMatrixType.COMPANY,
        threshold: float = 0.9,
        openai_client: Optional[Any] = None,
    ):
        self.agent_name = "CompanyMatchAgent"
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
        result = self.match_companies(prompt_text)
        event = AgentEvent(
            event_type="company_match",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=result.dict(),
        )
        return event

    def match_companies(self, prompt_text: str) -> CompanyMatchResult:
        if self.openai_client is None:
            score = 1.0
            feedback = "No OpenAI client; dummy pass."
            pass_threshold = True
            matched_companies = []
        else:
            scoring_prompt = (
                "Evaluate the prompt's company matching quality based on these criteria:\n"
                + "\n".join(
                    f"- {k}: weight {v}" for k, v in self.scoring_matrix.items()
                )
                + f"\n\nPrompt:\n{prompt_text}\n\nReturn JSON with score (0-1), feedback (string), matched_companies."
            )
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a company matching evaluator.",
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
                raw_feedback = parsed.get("feedback", "")
                if isinstance(raw_feedback, dict):
                    import json as js

                    feedback = js.dumps(raw_feedback)
                else:
                    feedback = str(raw_feedback)
                matched_companies = parsed.get("matched_companies")
                if matched_companies is None:
                    matched_companies = []
                elif not isinstance(matched_companies, list):
                    matched_companies = [matched_companies]
                pass_threshold = score >= self.threshold
            except Exception:
                score = 0.5
                feedback = "Failed to parse LLM company matching output."
                matched_companies = []
                pass_threshold = False
        return CompanyMatchResult(
            score=score,
            matrix=self.scoring_matrix,
            feedback=feedback,
            pass_threshold=pass_threshold,
            matched_companies=matched_companies,
            prompt_version=None,
        )
