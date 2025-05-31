# prompt_improvement_agent.py
"""
Prompt Improvement Agent (GPT-enhanced)

Purpose:
--------
Improves YAML-based LLM prompts based on structured feedback using OpenAI's GPT API.

Input:
------
- original_prompt: str
- feedback: dict (mit 'details', jedes mit 'dimension' und 'suggestion')

Output:
-------
- improved_prompt: str
- rationale: str
"""

import json
from typing import Tuple, Dict
from openai import OpenAI


class PromptImprovementAgent:
    def __init__(self, client: OpenAI, creative_mode: bool = False):
        self.client = client
        self.creative_mode = creative_mode

    def run(self, original_prompt: str, feedback: Dict) -> Tuple[str, str]:
        suggestions = feedback.get("details", [])
        if not suggestions:
            return (
                original_prompt,
                "No suggestions provided. Returning original prompt.",
            )

        system_prompt = (
            "You are an expert prompt engineer specializing in improving YAML-based LLM prompts. "
            "Your goal is to comprehensively improve the prompt by addressing all feedback suggestions. "
            "You may restructure, reword, and enhance clarity and effectiveness boldly."
        )

        if self.creative_mode:
            system_prompt += (
                " Apply advanced prompt engineering techniques. "
                "Rewrite sections fully for better flow, precision, and impact. "
                "Do not just add comments."
            )

        # Fasse Vorschläge kurz zusammen für das Modell
        summarized_suggestions = []
        for item in suggestions:
            dim = item.get("dimension", "unknown")
            sug = item.get("suggestion", "")
            if sug:
                summarized_suggestions.append(f"- {dim}: {sug}")

        user_prompt = (
            f"Feedback suggestions:\n" + "\n".join(summarized_suggestions) + "\n\n"
            f"Original prompt (YAML):\n{original_prompt}\n\n"
            f"Return only the improved YAML prompt, no explanations."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.6,
                max_tokens=1500,
            )
            improved_prompt = response.choices[0].message.content.strip()

            rationale = (
                "Improvements applied addressing feedback dimensions: "
                + ", ".join(
                    [
                        item.get("dimension", "unknown")
                        for item in suggestions
                        if item.get("suggestion")
                    ]
                )
            )

            return improved_prompt, rationale

        except Exception as e:
            return original_prompt, f"OpenAI API call failed: {e}"
