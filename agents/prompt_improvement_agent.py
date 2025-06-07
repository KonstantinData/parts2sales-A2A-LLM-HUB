""""""

"""
prompt_improvement_agent.py

Purpose : Improves prompts based on dynamic feedback from quality evaluation using LLM.
Logging : Logs all improvement events and errors into centralized workflow JSONL log via JsonlEventLogger.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Accepts dynamic, context-sensitive feedback for prompt improvement.
# - Supports both plain feedback and structured detailed_feedback from PromptQualityAgent.
# - Uses LLM to rewrite prompts guided by feedback.
# - Ensures all events are traceably logged per workflow/session.
# - Supports multiple improvement strategies for extensibility.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4
import re

from utils.time_utils import cet_now, timestamp_for_filename
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger
from utils.openai_client import OpenAIClient
from utils.prompt_versioning import extract_stage, extract_version
from utils.semantic_versioning_utils import update_version_in_yaml_string


def next_template_filename(prompt_path: Path, prompt_content: str):
    """Return filename for the v0.2.0 template and write the updated YAML."""
    stage = "template"
    new_version = "0.2.0"
    base_name = prompt_path.stem.split("_")[0]
    new_name = f"{base_name}_{stage}_v{new_version}.yaml"

    updated_content = update_version_in_yaml_string(prompt_content, new_version)
    new_path = Path("prompts/01-template") / new_name
    new_path.parent.mkdir(parents=True, exist_ok=True)

    with open(new_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    return new_path, extract_version(prompt_path.name), new_version, updated_content


class PromptImprovementAgent:
    def __init__(
        self,
        improvement_strategy,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        self.improvement_strategy = improvement_strategy
        self.llm = openai_client
        self.log_dir = log_dir

    def improve_prompt(self, prompt_content: str, feedback=None) -> str:
        if feedback is None:
            feedback = []
        if isinstance(feedback, str):
            feedback = [feedback]

        structured_sections = []
        for fb in feedback:
            if isinstance(fb, dict) and "position" in fb and "feedback" in fb:
                section = f"### Position: {fb['position']}\n{fb['feedback']}"
                structured_sections.append(section)
            elif isinstance(fb, str):
                structured_sections.append(f"- {fb}")

        feedback_section = "\n\n".join(structured_sections).strip()
        if not feedback_section:
            feedback_section = (
                "No explicit weaknesses detected. Please suggest at least one minor improvement in clarity, "
                "explicitness, conciseness, or formatting."
            )

        full_prompt = (
            "You are an expert prompt engineer.\n"
            "Review the following prompt and the structured feedback from a previous quality assessment.\n"
            "For each identified issue, rewrite the prompt to directly address it.\n"
            "Make your improvements clear and relevant. If no clear issue is found, improve clarity or format.\n\n"
            "Original prompt:\n"
            f"{prompt_content}\n\n"
            "Feedback:\n"
            f"{feedback_section}\n\n"
            "Rewritten prompt:"
        )

        response = self.llm.chat_completion(
            prompt=full_prompt,
            max_tokens=512,
            temperature=0.7,
        )

        improved_prompt = response.choices[0].message.get("content", "").strip()
        return improved_prompt or prompt_content

    def run(
        self,
        prompt_path: Path,
        base_name: str,
        iteration: int,
        workflow_id: str = None,
        feedback=None,
    ):
        if workflow_id is None:
            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()

            improved_prompt = self.improve_prompt(prompt_content, feedback=feedback)

            updated_path, old_version, new_version, improved_prompt = (
                next_template_filename(prompt_path, improved_prompt)
            )

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
                    "old_version": old_version,
                    "new_version": new_version,
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


""
