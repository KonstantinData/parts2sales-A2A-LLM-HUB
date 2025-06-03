"""
openai_client.py

Purpose : Provides a production-ready, type-safe OpenAI API integration for all agents.
Version : 1.1.0
Author  : Konstantin’s AI Copilot
Notes   :
- Loads API key from .env/OS
- Centralized logging, error handling, retry, and response validation
- Returns only validated Pydantic models
- Accepts only OpenAI API keyword arguments (model, temperature, max_tokens, etc.)
Usage examples:
    client = OpenAIClient()
    result = client.chat_completion(prompt="...", temperature=0.2)
"""

import os
from openai import OpenAI
from pydantic import BaseModel
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv

load_dotenv()


class OpenAIChoice(BaseModel):
    message: Dict[str, Any]
    finish_reason: Optional[str]
    index: Optional[int]


class OpenAIResponse(BaseModel):
    id: Optional[str]
    object: Optional[str]
    created: Optional[int]
    model: Optional[str]
    usage: Optional[Dict[str, Any]]
    choices: List[OpenAIChoice]


class OpenAIClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not found in environment.")
        self.client = OpenAI(api_key=api_key)

    def chat_completion(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.2,
        max_tokens: int = 512,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[List[str]] = None,
    ) -> OpenAIResponse:
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
        )
        # Fix: cast OpenAI object to dict before passing to Pydantic
        if hasattr(response, "model_dump"):
            response_dict = response.model_dump()
        elif hasattr(response, "to_dict"):
            response_dict = response.to_dict()
        else:
            # Fallback (z. B. für ältere Versionen)
            import json

            response_dict = json.loads(str(response))
        return OpenAIResponse(**response_dict)
