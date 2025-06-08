"""
Prompt Improvement Agent

Version: 2.0.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Improves weak sections of a prompt based on critical feedback returned
by the PromptQualityAgent. Uses OpenAIClient to rewrite only the
underperforming components. Generates a new versioned prompt file.
"""

from pathlib import Path
from utils.prompt_loader import load_prompt_file, save_prompt_file_with_new_version
from utils.logging import log_event
from agents.prompt_utils.rewrite_module import rewrite_prompt_sections
from typing import Dict, Any


class PromptImprovementAgent:
    def __init__(self, openai_client):
        self.openai_client = openai_client

    def improve_prompt(
        self, prompt_path: str, critical_feedback: Dict[str, str]
    ) -> str:
        # Notes: Load original prompt
        prompt_data = load_prompt_file(prompt_path)

        # Notes: Rewrite weak sections based on agent-specific feedback
        improved_prompt = rewrite_prompt_sections(
            prompt_data=prompt_data,
            feedback=critical_feedback,
            client=self.openai_client,
        )

        # Notes: Save improved prompt with bumped version number
        new_path = save_prompt_file_with_new_version(prompt_path, improved_prompt)

        # Notes: Log improvement step
        log_event(
            event_type="improvement",
            agent_name="PromptImprovementAgent",
            status="completed",
            payload={
                "original_path": str(prompt_path),
                "new_path": str(new_path),
                "feedback_used": critical_feedback,
            },
        )

        return str(new_path)
