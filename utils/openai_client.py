# utils/openai_client.py

"""
OpenAI Client Wrapper

Version: 2.0.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Centralized access to OpenAI chat completions.
Injectable in all agents via constructor.
"""

import openai
import os


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable.")
        openai.api_key = self.api_key

    def chat(self, prompt: str, model: str = "gpt-4", temperature: float = 0.2) -> str:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message["content"].strip()
