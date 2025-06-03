"""
prompt_improvement_agent.py

Purpose : Improves prompts using LLM and internal logic. Logs all events per workflow session as JSONL.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Centralized workflow-based JSONL logging (JsonlEventLogger).
# - Every agent action, including errors, is captured as an AgentEvent.
# - No scattered file writes, no legacy output – only one structured log per workflow.
# - Follows compliance, monitoring, and debugging best practices.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from utils.openai_client import OpenAIClient
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger


class PromptImprovementAgent:
    def __init__(
        self,
        improvement_strategy,
        openai_client: OpenAIClient,
        log_dir=Path("logs/workflows"),
    ):
        """
        improvement_strategy: defines how prompt improvement is performed (your own logic/type)
        openai_client: injected OpenAIClient instance
        log_dir: workflow log storage (default: logs/workflows)
        """
        self.improvement_strategy = improvement_strategy
        self.llm = openai_client
        self.log_dir = log_dir

    def run(
        self, prompt_path: Path, base_name: str, iteration: int, workflow_id: str = None
    ):
        """
        Entry point for prompt improvement task.
        All events are appended to the workflow JSONL log.
        """
        if workflow_id is None:
            workflow_id = f"{datetime.utcnow().isoformat(timespec='seconds').replace(':', '-')}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            # --- Read prompt
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()

            # --- Perform improvement (LLM or custom logic)
            improved_prompt = self.improve_prompt(prompt_content)

            payload = {
                "original_prompt": prompt_content,
                "improved_prompt": improved_prompt,
                "feedback": "",
            }

            # --- Log success event
            event = AgentEvent(
                event_type="prompt_improvement",
                agent_name="PromptImprovementAgent",
                agent_version="1.2.0",
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
                agent_version="1.2.0",
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

    def improve_prompt(self, prompt_content):
        """
        Your custom prompt improvement logic.
        Here: simple pass-through or LLM-based enhancement (replace this with real logic).
        """
        # Example: Just return prompt_content for now, or call self.llm with your logic.
        # improved = self.llm.improve_prompt(prompt_content)
        # return improved
        return prompt_content  # Placeholder
