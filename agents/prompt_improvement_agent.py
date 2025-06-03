"""
prompt_improvement_agent.py

Purpose : Improves prompts based on quality feedback using LLM or custom logic.
Logging : Logs all events (success and error) into a centralized JSONL workflow log via JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Accepts feedback from quality checks to inform improvements.
# - Uses injected OpenAIClient for LLM interactions.
# - Centralizes all event logging per workflow/session.
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
        improvement_strategy: defines the type of improvement logic ('LLM', 'RULE_BASED', etc.)
        openai_client: injected OpenAIClient instance
        log_dir: directory for workflow logs (default: logs/workflows)
        """
        self.improvement_strategy = improvement_strategy
        self.llm = openai_client
        self.log_dir = log_dir

    def run(
        self,
        prompt_path: Path,
        base_name: str,
        iteration: int,
        workflow_id: str = None,
        feedback: str = "",
    ):
        """
        Runs prompt improvement using the specified strategy and feedback.
        Logs all events to the centralized JSONL workflow log.
        """
        if workflow_id is None:
            workflow_id = f"{datetime.utcnow().isoformat(timespec='seconds').replace(':', '-')}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # Read current prompt content
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()

            # Improve prompt using feedback and strategy
            improved_prompt = self.improve_prompt(prompt_content, feedback)

            payload = {
                "original_prompt": prompt_content,
                "improved_prompt": improved_prompt,
                "feedback": feedback,
            }

            event = AgentEvent(
                event_type="prompt_improvement",
                agent_name="PromptImprovementAgent",
                agent_version="1.3.1",
                timestamp=datetime.utcnow(),
                step_id="improvement",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "improvement_strategy": str(self.improvement_strategy),
                },
            )
            logger.log_event(event)
            return event

        except Exception as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="PromptImprovementAgent",
                agent_version="1.3.1",
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
                    "improvement_strategy": str(self.improvement_strategy),
                },
            )
            logger.log_event(error_event)
            raise

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

        improved_prompt = ""
        if response.choices and len(response.choices) > 0:
            choice = response.choices[0]
            if hasattr(choice, "message") and hasattr(choice.message, "content"):
                improved_prompt = choice.message.content.strip()
            elif hasattr(choice, "text"):
                improved_prompt = choice.text.strip()

        if not improved_prompt:
            improved_prompt = prompt_content

        return improved_prompt
