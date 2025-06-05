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

from utils.time_utils import cet_now
import re

from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient
from utils.prompt_versioning import extract_stage, extract_version, bump_version


def next_patch_filename(prompt_path: Path) -> Path:
    """
    Generates next patch version filename for a prompt.
    E.g. 'feature_setup_raw_v0.1.0.yaml' → 'feature_setup_raw_v0.1.1.yaml'
    """
    orig_name = prompt_path.name
    stage = extract_stage(orig_name)
    version = extract_version(orig_name)
    new_version = bump_version(version, mode="patch")
    new_name = re.sub(rf"_{stage}_v{version}", f"_{stage}_v{new_version}", orig_name)
    return prompt_path.parent / new_name


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

    def improve_prompt(self, prompt_content: str, feedback=None) -> str:
        """
        Use LLM to improve the prompt based on quality feedback.
        If feedback is empty or unspecific, propose at least one micro-improvement.

        Args:
            prompt_content: Original prompt text.
            feedback: List of feedback strings from quality evaluation.

        Returns:
            Improved prompt text.
        """
        if feedback is None:
            feedback = []
        if isinstance(feedback, str):
            feedback = [feedback]
        feedback_section = "\n".join(f"- {fb}" for fb in feedback if fb.strip())
        if not feedback_section:
            feedback_section = "No explicit weaknesses detected. Please suggest at least one minor improvement in clarity, explicitness, conciseness, or formatting."

        full_prompt = (
            "You are an expert prompt engineer.\n"
            "Review the following prompt and the given feedback from a previous quality assessment.\n"
            "For each identified weakness, rewrite the prompt to directly address the point, making your changes explicit and relevant.\n"
            "If the feedback is empty or unspecific, propose at least one minor improvement to clarity, explicitness, conciseness, or formatting.\n"
            "Clearly reference required output formats, instructions, and examples if mentioned in the feedback.\n"
            "Original prompt:\n"
            f"{prompt_content}\n\n"
            "Feedback (quality agent findings):\n"
            f"{feedback_section}\n\n"
            "Please rewrite the prompt so that every criticism from the feedback is resolved, or, if no criticisms are present, suggest one incremental improvement."
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
        feedback=None,
    ):
        """
        Runs the prompt improvement process.
        Logs all events into the centralized workflow JSONL log.
        """
        if workflow_id is None:
            workflow_id = f"{cet_now().isoformat(timespec='seconds').replace(':', '-')}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()

            improved_prompt = self.improve_prompt(prompt_content, feedback=feedback)

            updated_path = next_patch_filename(prompt_path)
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
                timestamp=cet_now(),
                step_id="improvement",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                    "improvement_strategy": self.improvement_strategy,
                    "updated_path": str(updated_path),
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
                timestamp=cet_now(),
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
