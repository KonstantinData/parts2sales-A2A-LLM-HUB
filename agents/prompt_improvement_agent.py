"""
prompt_improvement_agent.py

Purpose : Improves prompts based on dynamic feedback from quality evaluation using LLM.
Logging : Logs all improvement events and errors into centralized workflow JSONL log via JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Accepts dynamic, context-sensitive feedback for prompt improvement.
# - Uses LLM to rewrite prompts guided by feedback.
# - Ensures all events are traceably logged per workflow/session.
# - Supports multiple improvement strategies for extensibility.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient


class PromptImprovementAgent:
    def __init__(
        self,
        improvement_strategy,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        """
        improvement_strategy: logic or type for prompt improvement (e.g., 'LLM', 'RULE_BASED', etc.)
        openai_client: injected OpenAIClient instance
        log_dir: workflow log storage (default: logs/workflows)
        """
        self.improvement_strategy = improvement_strategy
        self.llm = openai_client
        self.log_dir = log_dir

    def improve_prompt(self, prompt_content: str, feedback: str = "") -> str:
        """
        Use LLM to improve the prompt based on quality feedback.

        Args:
            prompt_content: Original prompt text.
            feedback: Feedback string from quality evaluation describing weaknesses.

        Returns:
            Improved prompt text.
        """

        full_prompt = (
            "You are a prompt engineer. Improve the given prompt using the feedback.\n\n"
            f"Original prompt:\n{prompt_content}\n\n"
            f"Feedback:\n{feedback}\n\n"
            "Please rewrite the prompt to address the feedback."
        )

        response = self.llm.chat_completion(
            prompt=full_prompt,
            max_tokens=512,
            temperature=0.7,
        )

        improved_prompt = response.choices[0].message.get("content", "").strip()

        if not improved_prompt:
            improved_prompt = prompt_content

        return improved_prompt

    def run(
        self,
        prompt_path: Path,
        base_name: str,
        iteration: int,
        workflow_id: str = None,
        feedback: str = "",
    ):
        """
        Runs the prompt improvement process.
        Logs all events into the centralized workflow JSONL log.
        """
        if workflow_id is None:
            workflow_id = f"{datetime.utcnow().isoformat(timespec='seconds').replace(':', '-')}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # Read current prompt
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()

            # Improve prompt using LLM guided by feedback
            improved_prompt = self.improve_prompt(prompt_content, feedback=feedback)

            # Optionally, save improved prompt to a new file (not mandatory)
            updated_path = (
                prompt_path.parent / f"{base_name}_improved_iter{iteration}.yaml"
            )
            with open(updated_path, "w", encoding="utf-8") as f:
                f.write(improved_prompt)

            payload = {
                "original_prompt": prompt_content,
                "improved_prompt": improved_prompt,
                "updated_path": str(updated_path),
                "feedback_used": feedback,
            }

            event = AgentEvent(
                event_type="prompt_improvement",
                agent_name="PromptImprovementAgent",
                agent_version="1.0.0",
                timestamp=datetime.utcnow(),
                step_id="improvement",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "improvement_strategy": self.improvement_strategy,
                },
            )
            logger.log_event(event)
            return event

        except Exception as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="PromptImprovementAgent",
                agent_version="1.0.0",
                timestamp=datetime.utcnow(),
                step_id="improvement",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                    "improvement_strategy": self.improvement_strategy,
                },
            )
            logger.log_event(error_event)
            raise
