"""
controller_agent.py

Purpose : Orchestrates workflow steps across multiple agents. Ensures all agent events (including errors) are logged per workflow/session in a central JSONL log.

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Centralized workflow-based JSONL logging (JsonlEventLogger).
# - Every workflow control, delegation, and error is logged as a structured AgentEvent.
# - No legacy or scattered file output, only compliant, scalable per-session logging.
# - Ideal for monitoring, debugging, and auditing complex workflows.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger


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
            workflow_id = f"{datetime.utcnow().isoformat(timespec='seconds').replace(':', '-')}_workflow_{uuid4().hex[:6]}"
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
                        timestamp=datetime.utcnow(),
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

                # Log delegation event
                delegation_event = AgentEvent(
                    event_type="controller_delegate",
                    agent_name="ControllerAgent",
                    agent_version="1.0.0",
                    timestamp=datetime.utcnow(),
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
                # Log agent return event if not already logged inside agent
                # (Optional: Can be skipped if subagents handle their own logging.)

            # Workflow completed event
            completion_event = AgentEvent(
                event_type="workflow_complete",
                agent_name="ControllerAgent",
                agent_version="1.0.0",
                timestamp=datetime.utcnow(),
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
                timestamp=datetime.utcnow(),
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
