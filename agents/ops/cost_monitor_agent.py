"""
cost_monitor_agent.py

Purpose : Monitors, aggregates, and reports LLM API costs and token usage during workflow runs.
Version : 0.1.0-raw
Author  : Konstantin & AI Copilot
Notes   :
- Designed for pluggable cost tracking across prompt lifecycle/agents.
- Supports per-agent and total workflow cost reporting.
- Integrates with OpenAI client responses (token usage, pricing).

Example:
    agent = CostMonitorAgent()
    event = agent.run(agent_name="PromptQualityAgent", tokens_used=1054, cost=0.003, meta={...})
"""

from typing import Dict, Any, Optional
from agents.utils.schemas import AgentEvent
from datetime import datetime


class CostMonitorAgent:
    def __init__(self):
        self.agent_name = "CostMonitorAgent"
        self.agent_version = "0.1.0-raw"
        self.total_cost = 0.0
        self.total_tokens = 0

    def run(
        self,
        agent_name: str,
        tokens_used: int,
        cost: float,
        prompt_version: Optional[str] = None,
        step_id: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> AgentEvent:
        self.total_cost += cost
        self.total_tokens += tokens_used

        payload = {
            "agent_name": agent_name,
            "tokens_used": tokens_used,
            "cost": cost,
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
        }

        return AgentEvent(
            event_type="cost_monitoring",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=step_id or "cost_monitoring",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )
