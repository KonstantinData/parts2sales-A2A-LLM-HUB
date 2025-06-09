"""
utils/openai_client.py

Purpose : Centralized OpenAI client wrapper with .env support (v1.x compatible).
Version : 2.1.0
Author  : Konstantin Milonas with Agentic AI Copilot support
"""

from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables from .env (if present)
load_dotenv(override=True)


class OpenAIClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=api_key)

    def chat(
        self,
        prompt: str,
        model: str = "gpt-4-turbo",
        temperature: float = 0.2,
        force_json: bool = True,
    ) -> str:
        # Only gpt-4-turbo and gpt-3.5-turbo-1106+ support response_format
        kwargs = {}
        if force_json:
            kwargs["response_format"] = {"type": "json_object"}
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.content.strip()
