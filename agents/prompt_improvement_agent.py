#!/usr/bin/env python3
"""
File: prompt_improvement_agent.py
Type: Python Module (Agent Implementation)

Purpose:
--------
This module implements the PromptImprovementAgent, which uses GPT-4 via OpenAI API
to revise YAML prompts based on structured feedback from a validation agent.

Usage:
------
Used after a prompt fails quality evaluation to generate an improved version,
following best practices for clarity, structure, tone, and robustness.

Notes:
------
- Requires a valid OpenAI API key in environment (via .env or OS settings)
- Returns a string representing the improved YAML prompt content
"""

import os
from agents.base_agent import BaseAgent
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


class PromptImprovementAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="PromptImprovementAgent")

    def run(self, prompt_text: str, feedback_json: str) -> str:
        """
        Use GPT-4 to generate an improved version of the prompt based on feedback.

        Args:
            prompt_text (str): Original YAML prompt text
            feedback_json (str): Feedback report in JSON string format

        Returns:
            str: Improved YAML prompt text
        """
        improvement_instruction = f"""
You are an experienced prompt engineer.

Your task: Improve the YAML prompt below based on the structured feedback from a quality validation tool.

🧾 Feedback:
{feedback_json}

🧱 Original Prompt:
{prompt_text}

🎯 Your goal is to improve:
- Clarity: use precise, unambiguous wording
- Structure: ensure logical flow, steps, or blocks
- Robustness: prevent edge case failures
- LLM-compatibility: avoid idioms, vague terms, or ambiguous slots
- Formal tone and grammar: correct stylistic issues

📌 Constraints:
- Do not change the core intent of the original prompt.
- Return **only** the improved YAML content – no prose or explanations.
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced prompt engineer.",
                },
                {"role": "user", "content": improvement_instruction},
            ],
        )

        improved_yaml = response.choices[0].message.content.strip()
        return improved_yaml
