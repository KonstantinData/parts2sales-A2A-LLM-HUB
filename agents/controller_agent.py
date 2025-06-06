"""
controller_agent.py

Purpose : Orchestrates workflow steps across multiple agents. Ensures all agent events (including errors) are logged per workflow/session in a central JSONL log.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Centralized workflow-based JSONL logging (JsonlEventLogger).
# - Every workflow control, delegation, and error is logged as a structured AgentEvent.
# - Orchestrates agent execution via an injected agent_registry.
# - Only workflow-centric, append-only JSONL output – compliant & auditable.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from utils.time_utils import cet_now, timestamp_for_filename

from utils.schemas import AgentEvent, RawPrompt
from utils.jsonl_event_logger import JsonlEventLogger
import yaml
from pydantic import ValidationError


class ControllerAgent:
    def __init__(self, agent_registry: dict, log_dir=Path("logs/workflows")):
        """
        agent_registry: dict mapping step/type to agent instances (DI)
        log_dir: base directory for workflow logs (default: logs/workflows)
        """
        self.agent_registry = agent_registry
        self.log_dir = log_dir

    def run(self, workflow_steps: list, workflow_id: str = None, meta: dict = None):
        """
        Orchestrates the sequence of agent actions as defined in workflow_steps.
        All events are logged into the workflow JSONL file.
        """
        if workflow_id is None:
            workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)
        meta = meta or {}

        try:
            for step_idx, step in enumerate(workflow_steps):
                step_type = step.get("type")
                agent = self.agent_registry.get(step_type)
                if agent is None:
                    # Log error for missing agent
                    error_event = AgentEvent(
                        event_type="error",
                        agent_name="ControllerAgent",
                        agent_version="1.0.0",
                        timestamp=cet_now(),
                        step_id=f"controller_step_{step_idx}",
                        prompt_version=None,
                        status="error",
                        payload={
                            "exception": f"No agent registered for step type '{step_type}'",
                        },
                        meta={
                            "step": step,
                            "meta": meta,
                        },
                    )
                    logger.log_event(error_event)
                    raise ValueError(f"No agent registered for step type '{step_type}'")

                # Validate prompt file if provided
                params = step.get("params", {})
                prompt_path = params.get("prompt_path")
                if prompt_path:
                    try:
                        with open(prompt_path, "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f) or {}
                        RawPrompt(**data)
                    except ValidationError as ve:
                        step_copy = step.copy()
                        step_params = step_copy.get("params", {}).copy()
                        if "prompt_path" in step_params:
                            step_params["prompt_path"] = str(step_params["prompt_path"])
                        step_copy["params"] = step_params
                        error_event = AgentEvent(
                            event_type="error",
                            agent_name="ControllerAgent",
                            agent_version="1.0.0",
                            timestamp=cet_now(),
                            step_id=f"controller_step_{step_idx}",
                            prompt_version=None,
                            status="error",
                            payload={
                                "exception": f"Prompt validation failed for {prompt_path}",
                                "details": str(ve),
                            },
                            meta={"step": step_copy, "meta": meta},
                        )
                        logger.log_event(error_event)
                        raise ValueError(f"Prompt validation failed for {prompt_path}: {ve}")

                # Log delegation event
                delegation_event = AgentEvent(
                    event_type="controller_delegate",
                    agent_name="ControllerAgent",
                    agent_version="1.0.0",
                    timestamp=cet_now(),
                    step_id=f"controller_step_{step_idx}",
                    prompt_version=step.get("prompt_version"),
                    status="in_progress",
                    payload={
                        "message": f"Delegating to {agent.__class__.__name__}",
                        "step": step,
                    },
                    meta=meta,
                )
                logger.log_event(delegation_event)

                # Execute agent step (pass workflow_id through!)
                agent_event = agent.run(**step["params"], workflow_id=workflow_id)
                # Optionally log agent return (if not already logged inside agent)

            # Workflow completed event
            completion_event = AgentEvent(
                event_type="workflow_complete",
                agent_name="ControllerAgent",
                agent_version="1.0.0",
                timestamp=cet_now(),
                step_id="controller_done",
                prompt_version=None,
                status="success",
                payload={
                    "message": "Workflow completed successfully",
                },
                meta=meta,
            )
            logger.log_event(completion_event)
            return completion_event

        except Exception as ex:
            import traceback

            error_event = AgentEvent(
                event_type="error",
                agent_name="ControllerAgent",
                agent_version="1.0.0",
                timestamp=cet_now(),
                step_id="controller_error",
                prompt_version=None,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta=meta,
            )
            logger.log_event(error_event)
            raise
