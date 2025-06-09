# agents/ops/cost_monitor_agent.py

"""
Cost Monitor Agent

Version: 2.1.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Monitors OpenAI API usage and cost for the current workflow session.
Logs usage and estimated cost to the workflow-centric JSONL log.
"""

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, ValidationError
from utils.time_utils import cet_now
from utils.schemas import AgentEvent
from utils.jsonl_event_logger import JsonlEventLogger


class CostMonitorResult(BaseModel):
    """Schema for cost and usage logging."""

    total_tokens: int
    estimated_cost: float


class CostMonitorAgent:
    def __init__(
        self,
        log_dir=Path("logs/workflows"),
    ):
        self.log_dir = log_dir

    def run(
        self,
        total_tokens: int,
        estimated_cost: float,
        base_name: str,
        iteration: int,
        workflow_id: str = None,
        parent_event_id: str = None,
    ):
        if workflow_id is None:
            workflow_id = f"cost_{uuid4().hex[:6]}"
        logger = JsonlEventLogger(workflow_id, self.log_dir)

        try:
            validated = CostMonitorResult(
                total_tokens=total_tokens,
                estimated_cost=estimated_cost,
            )

            payload = {
                "total_tokens": validated.total_tokens,
                "estimated_cost": validated.estimated_cost,
            }

            event = AgentEvent(
                event_id=str(uuid4()),
                event_type="cost_monitor",
                agent_name="CostMonitorAgent",
                agent_version="2.1.0",
                timestamp=cet_now(),
                step_id="cost_monitor",
                prompt_version=base_name,
                status="success",
                payload=payload,
                meta={
                    "iteration": iteration,
                },
                workflow_id=workflow_id,
                source_event_id=parent_event_id,
            )
            logger.log_event(event)
            return event

        except (ValidationError, Exception) as ex:
            import traceback

            error_event = AgentEvent(
                event_id=str(uuid4()),
                event_type="error",
                agent_name="CostMonitorAgent",
                agent_version="2.1.0",
                timestamp=cet_now(),
                step_id="cost_monitor",
                prompt_version=base_name,
                status="error",
                payload={
                    "exception": str(ex),
                    "traceback": traceback.format_exc(),
                },
                meta={
                    "iteration": iteration,
                },
                workflow_id=workflow_id,
                source_event_id=parent_event_id,
            )
            logger.log_event(error_event)
            raise
