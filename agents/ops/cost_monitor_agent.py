"""
cost_monitor_agent.py

Purpose : Monitors and logs OpenAI API token/cost usage for agentic workflows.
Version : 1.0.1
Author  : Konstantin & AI Copilot
Notes   :
- Aggregates API call costs by agent and run.
- Logs all cost events exclusively to logs/weighted_score/
- Designed for integration into pipeline or as a CLI utility.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from utils.schemas import AgentEvent
from utils.event_logger import write_event_log
from pathlib import Path

LOG_DIR = Path("logs") / "weighted_score"


class CostMonitorAgent:
    def __init__(self):
        self.agent_name = "CostMonitorAgent"
        self.agent_version = "1.0.1"

    def log_cost(
        self,
        tokens_used: int,
        cost_usd: float,
        agent: str,
        operation: str,
        base_name: str,
        iteration: int,
        prompt_version: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> AgentEvent:
        payload = {
            "tokens_used": tokens_used,
            "cost_usd": cost_usd,
            "operation": operation,
            "agent": agent,
        }
        event = AgentEvent(
            event_type="cost_monitor",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )
        write_event_log(LOG_DIR, event)
        return event
