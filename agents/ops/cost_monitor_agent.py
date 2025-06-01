"""
CostMonitorAgent

Monitors API usage (tokens, costs) and optionally cache statistics.
Returns results as AgentEvent with CostMonitorResult as payload.

Notes:
------
- Reads from OpenAI usage endpoints and (optionally) Redis/memory cache.
- Logs all cost/usage metrics as events (easy to push to analytics/monitoring).
- Can be called periodically (batch run, scheduled job, etc.).
"""

import os
import time
from typing import Any, Dict, Optional
from agents.utils.schemas import AgentEvent, BaseModel, Field


class CostMonitorResult(BaseModel):
    """
    Result schema for cost and usage monitoring.
    """

    period: str = Field(
        ..., description="Reporting period (e.g. '2024-06-07', 'batch_15', ...)"
    )
    total_tokens: int = Field(..., description="Total tokens used in period")
    total_cost_usd: float = Field(..., description="Total OpenAI API cost (USD)")
    cache_hitrate: Optional[float] = Field(
        None, description="Cache hitrate if available"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional monitoring details (per-model usage, etc.)",
    )


class CostMonitorAgent:
    def __init__(
        self,
        openai_client,
        cache=None,
        agent_name="CostMonitorAgent",
        agent_version="1.0",
    ):
        self.openai = openai_client
        self.cache = cache  # Optional: pass Redis or cache interface
        self.agent_name = agent_name
        self.agent_version = agent_version

    def run(
        self, period: str, prompt_version: str = None, meta: dict = None
    ) -> AgentEvent:
        """
        Collects and logs cost/usage metrics for the specified period.
        """
        meta = meta or {}
        total_tokens, total_cost_usd, details = self._collect_openai_usage(period)
        cache_hitrate = self._get_cache_hitrate() if self.cache else None
        result = CostMonitorResult(
            period=period,
            total_tokens=total_tokens,
            total_cost_usd=total_cost_usd,
            cache_hitrate=cache_hitrate,
            details=details,
        )
        event = AgentEvent(
            event_type="cost_monitor",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            step_id=meta.get("step_id", ""),
            prompt_version=prompt_version,
            meta=meta,
            payload=result.dict(),
        )
        return event

    def _collect_openai_usage(self, period: str):
        """
        Example: Collects usage from OpenAI API for this account.
        Replace with real usage collection as needed (organization, team, etc.).
        """
        # This is an example! Replace with your real org/usage API as needed.
        usage = (
            self.openai.api_usage()
        )  # Replace by actual usage endpoint if available!
        total_tokens = usage.get("total_tokens", 0)
        total_cost = usage.get("total_cost", 0.0)
        return total_tokens, total_cost, usage

    def _get_cache_hitrate(self):
        """
        Example: Collect cache stats (from Redis or memory cache).
        """
        if hasattr(self.cache, "info"):
            stats = self.cache.info()
            hits = stats.get("keyspace_hits", 0)
            misses = stats.get("keyspace_misses", 0)
            total = hits + misses
            return hits / total if total else None
        return None
