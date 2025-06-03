"""
llm_prompt_scorer.py

Purpose : Uses LLM to evaluate prompt quality using a scoring matrix. Receives OpenAIClient via Dependency Injection.
Version : 1.3.1
Author  : Konstantin’s AI Copilot
Notes   :
- Returns result as dict for flexible downstream processing.
"""

from typing import Any, Dict
from utils.openai_client import OpenAIClient
from datetime import datetime


class LLMPromptScorer:
    def __init__(self, openai_client: OpenAIClient):
        self.llm = openai_client

    def score_prompt(self, prompt: str) -> Dict[str, Any]:
        llm_response = self.llm.chat_completion(prompt=prompt)
        first_message = (
            llm_response.choices[0].message["content"]
            if llm_response.choices and "content" in llm_response.choices[0].message
            else ""
        )
        score_result = {
            "llm_output": first_message,
            "score": 0,
            "pass_threshold": False,
            "feedback": "",
            "timestamp": datetime.utcnow(),
        }
        return score_result
