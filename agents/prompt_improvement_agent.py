"""
PromptImprovementAgent

This agent receives a prompt and quality feedback, then generates an improved prompt
(based on LLM or rule-based methods). Always returns a structured AgentEvent with ImprovementResult.

Notes:
------
- Designed to be called in prompt improvement loops.
- Uses OpenAI for LLM-based rewriting (can fallback to dummy-mode for testing).
- All output is an AgentEvent (full audit trail, versioning, meta).
"""

from typing import Any, Dict
from datetime import datetime
from agents.utils.schemas import AgentEvent, ImprovementResult


class PromptImprovementAgent:
    def __init__(
        self,
        openai_client,
        agent_name="PromptImprovementAgent",
        agent_version="1.0",
        creative_mode=True,
    ):
        self.openai = openai_client
        self.agent_name = agent_name
        self.agent_version = agent_version
        self.creative_mode = creative_mode  # Use LLM, or dummy mode

    def run(
        self,
        prompt_text: str,
        quality_event: Dict[str, Any],
        prompt_version: str = None,
        meta: dict = None,
        method: str = "llm",
    ) -> AgentEvent:
        """
        Improve the given prompt based on quality feedback.
        Returns an AgentEvent with ImprovementResult.
        """
        meta = meta or {}

        if self.creative_mode and method == "llm":
            improved_prompt, rationale, changes = self._improve_with_llm(
                prompt_text, quality_event
            )
        else:
            improved_prompt, rationale, changes = self._improve_dummy(
                prompt_text, quality_event
            )

        result = ImprovementResult(
            improved_prompt=improved_prompt,
            rationale=rationale,
            changes=changes,
            prompt_version=prompt_version,
        )

        event = AgentEvent(
            event_type="prompt_improvement",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            step_id=meta.get("step_id", ""),
            prompt_version=prompt_version,
            meta=meta,
            payload=result.dict(),
        )
        return event

    def _improve_with_llm(self, prompt_text, quality_event):
        """
        Uses OpenAI LLM to improve the prompt.
        """
        feedback = quality_event.get("feedback", "")
        # Compose improvement instruction
        system_prompt = (
            "You are a prompt engineer. Rewrite the following prompt to maximize clarity, completeness, and instructional quality. "
            "Incorporate this feedback for improvement: "
            f"{feedback}\n\nPrompt:\n{prompt_text}\n\nReturn only the improved prompt text."
        )
        response = self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=800,
            temperature=0.7,
        )
        improved_prompt = response.choices[0].message.content.strip()
        rationale = f"Improved per feedback: {feedback}"
        changes = ["LLM rewrite", "Incorporated reviewer feedback"]
        return improved_prompt, rationale, changes

    def _improve_dummy(self, prompt_text, quality_event):
        """
        Dummy fallback: Append feedback to the prompt.
        """
        feedback = quality_event.get("feedback", "")
        improved_prompt = prompt_text + "\n# Improvement:\n" + feedback
        rationale = "Appended feedback as dummy improvement."
        changes = ["Appended feedback"]
        return improved_prompt, rationale, changes
