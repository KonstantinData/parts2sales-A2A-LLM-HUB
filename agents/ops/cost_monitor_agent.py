"""
cost_monitor_agent.py

Purpose : Monitors and logs API and resource costs per agent/process step.
Version : 1.1.0
Author  : Konstantin & AI Copilot
Notes   :
- Aggregates cost metadata (tokens, API $) for workflow auditing.
- Can be extended to enforce cost budgets and trigger alerts.
- Emits AgentEvent with cost breakdown for traceability.
- Use as a decorator or call after LLM/agent runs.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from utils.schema import AgentEvent


class CostMonitorAgent:
    def __init__(self):
        self.agent_name = "CostMonitorAgent"
        self.agent_version = "1.1.0"

    def run(
        self,
        cost_data: Dict[str, Any],
        base_name: str,
        iteration: int,
        prompt_version: str = None,
        meta: Dict[str, Any] = None,
    ) -> AgentEvent:
        """
        cost_data example:
        {
            "prompt_tokens": 1024,
            "completion_tokens": 512,
            "api_cost_usd": 0.0042,
            "agent_name": "PromptQualityAgent",
            "step_type": "quality_check"
        }
        """
        payload = {"costs": cost_data, "info": "Resource and API costs for this step."}
        event = AgentEvent(
            event_type="cost_monitoring",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=f"{base_name}_v{prompt_version}_it{iteration}",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )
        return event
