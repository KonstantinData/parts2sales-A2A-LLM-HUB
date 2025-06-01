"""
CRMSyncAgent

Syncs matched companies or contacts to a CRM (e.g., HubSpot or test endpoint).
Uses Strategy-Pattern: target system selected by ENV/config.

Notes:
------
- ENV var `CRM_MODE` controls which strategy is used (hubspot, test, ...).
- Extend easily for more CRMs or webhook endpoints.
- Returns all results as AgentEvent with CRMSyncResult as payload.
"""

import os
import requests
from typing import Any, Dict, List
from agents.utils.schemas import AgentEvent, BaseModel, Field


class CRMSyncResult(BaseModel):
    """
    Result schema for CRM sync operation.
    """

    status: str = Field(..., description="Result: success, warning, error")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Sync/response details (IDs, errors, etc.)"
    )
    crm_mode: str = Field(
        ..., description="Which CRM system/strategy was used (e.g., 'hubspot', 'test')"
    )
    rationale: str = Field(..., description="Explanation (or error message) for result")


class CRMSyncAgent:
    def __init__(self, agent_name="CRMSyncAgent", agent_version="1.0"):
        self.agent_name = agent_name
        self.agent_version = agent_version
        self.crm_mode = os.getenv("CRM_MODE", "test").lower()
        self.hubspot_api_key = os.getenv("HUBSPOT_API_KEY", "")
        # Extend: add other CRM/API keys as needed

    def run(
        self,
        company_data: List[Dict[str, Any]],
        prompt_version: str = None,
        meta: dict = None,
    ) -> AgentEvent:
        """
        Sync company data to the selected CRM system.
        """
        meta = meta or {}
        if self.crm_mode == "hubspot":
            status, details, rationale = self._sync_to_hubspot(company_data)
        else:
            status, details, rationale = self._sync_to_test(company_data)
        result = CRMSyncResult(
            status=status,
            details=details,
            crm_mode=self.crm_mode,
            rationale=rationale,
        )
        event = AgentEvent(
            event_type="crm_sync",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            step_id=meta.get("step_id", ""),
            prompt_version=prompt_version,
            meta=meta,
            payload=result.dict(),
        )
        return event

    def _sync_to_hubspot(self, companies):
        """
        Real sync with HubSpot. Extend as needed.
        """
        url = "https://api.hubapi.com/crm/v3/objects/companies"
        headers = {
            "Authorization": f"Bearer {self.hubspot_api_key}",
            "Content-Type": "application/json",
        }
        results = []
        try:
            for company in companies:
                resp = requests.post(url, headers=headers, json={"properties": company})
                if resp.status_code == 201:
                    results.append(
                        {"id": resp.json().get("id"), "name": company.get("name")}
                    )
                else:
                    results.append({"error": resp.text, "company": company.get("name")})
            status = "success" if all("id" in r for r in results) else "warning"
            rationale = (
                "All companies synced"
                if status == "success"
                else "Some companies failed"
            )
            return status, {"results": results}, rationale
        except Exception as e:
            return "error", {"exception": str(e)}, f"Exception during HubSpot sync: {e}"

    def _sync_to_test(self, companies):
        """
        Dummy/test sync (just logs, returns fake IDs).
        """
        results = [
            {"id": f"test_{i}", "name": c.get("name")} for i, c in enumerate(companies)
        ]
        return "success", {"results": results}, "Test mode: no real sync performed."
