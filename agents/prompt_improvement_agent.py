"""
prompt_improvement_agent.py

Purpose : Agent for improving prompts based on LLM feedback and weighted rationale.
Version : 1.1.3
Author  : Konstantin & AI Copilot
Notes   :
- Receives meta/feedback, uses OpenAI LLM for guided rewriting (kein Dummy!).
- Logs all improvement events exklusiv nach logs/weighted_score/
- Usage:
    agent = PromptImprovementAgent(openai_client=client)
    agent.run(prompt_text, feedback, base_name, iteration, prompt_version)
"""

from typing import Optional, Any
from datetime import datetime
from utils.schema import AgentEvent
from utils.event_logger import write_event_log
from pathlib import Path

LOG_DIR = Path("logs") / "weighted_score"


class PromptImprovementAgent:
    def __init__(
        self,
        openai_client: Optional[Any] = None,
    ):
        self.agent_name = "PromptImprovementAgent"
        self.agent_version = "1.1.3"
        self.openai_client = openai_client

    def run(
        self,
        prompt_text: str,
        feedback: str,
        base_name: str,
        iteration: int,
        prompt_version: Optional[str] = None,
        meta: Optional[dict] = None,
    ) -> AgentEvent:
        improved, rationale = self.improve_prompt(prompt_text, feedback)
        event = AgentEvent(
            event_type="prompt_improvement",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload={
                "improved_prompt": improved,
                "rationale": rationale,
                "feedback": feedback,
            },
        )
        write_event_log(event)
        return event

    def improve_prompt(self, prompt_text: str, feedback: str):
        """
        Actually uses the LLM (OpenAI) to rewrite prompt based on feedback.
        """
        if self.openai_client is None:
            improved = prompt_text + "\n# [No OpenAI client: No improvement applied]"
            rationale = "OpenAI client not set; dummy improvement only."
        else:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert prompt engineer. Your task is to rewrite the given prompt according to the feedback. Return ONLY the improved prompt as markdown code block. Short rationale after.",
                    },
                    {
                        "role": "user",
                        "content": f"Prompt to improve:\n{prompt_text}\n\nImprovement feedback:\n{feedback}",
                    },
                ],
                temperature=0.3,
                max_tokens=512,
            )
            improved = response.choices[0].message.content.strip()
            rationale = f"LLM rewrite. Model: gpt-4-turbo, feedback: {feedback}"
        return improved, rationale
