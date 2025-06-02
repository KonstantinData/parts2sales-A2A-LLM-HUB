"""
crm_sync_agent.py

Purpose : Synchronizes and enriches prompt workflow data with HubSpot CRM via API.
Version : 0.1.0-raw
Author  : Konstantin & AI Copilot
Notes   :
- Pushes structured results (matches, use cases, features, etc.) to HubSpot objects (Company, Contact, Deal).
- Pulls reference data (Company lists, Properties) for matching or enrichment.
- Handles auth and error logging.
- Returns AgentEvent with operation status and result summary.

Example:
    agent = CRMSyncAgent(api_key=HUBSPOT_KEY)
    event = agent.run(object_type="company", data={...}, action="upsert")
"""

from typing import Dict, Any, Optional
from agents.utils.schemas import AgentEvent
from datetime import datetime
import requests
import os


class CRMSyncAgent:
    def __init__(self, api_key: str = None):
        self.agent_name = "CRMSyncAgent"
        self.agent_version = "0.1.0-raw"
        self.api_key = api_key or os.getenv("HUBSPOT_API_KEY")
        self.base_url = "https://api.hubapi.com"

    def run(
        self,
        object_type: str,  # "company", "contact", "deal"
        data: Dict[str, Any],
        action: str = "upsert",  # "create", "update", "upsert"
        prompt_version: Optional[str] = None,
        step_id: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> AgentEvent:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        endpoint = self._build_endpoint(object_type, action)
        result = {}
        status = "success"
        try:
            resp = requests.post(endpoint, headers=headers, json=data)
            result = resp.json()
            if not resp.ok:
                status = "failed"
        except Exception as e:
            result = {"error": str(e)}
            status = "failed"

        payload = {
            "object_type": object_type,
            "action": action,
            "status": status,
            "hubspot_response": result,
        }

        return AgentEvent(
            event_type="crm_sync",
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            timestamp=datetime.utcnow(),
            step_id=step_id or "crm_sync",
            prompt_version=prompt_version,
            meta=meta or {},
            payload=payload,
        )

    def _build_endpoint(self, object_type: str, action: str) -> str:
        # Simple endpoint logic for HubSpot v3 objects API
        if object_type == "company":
            return f"{self.base_url}/crm/v3/objects/companies"
        if object_type == "contact":
            return f"{self.base_url}/crm/v3/objects/contacts"
        if object_type == "deal":
            return f"{self.base_url}/crm/v3/objects/deals"
        # Fallback: raise error
        raise ValueError(f"Unsupported object_type: {object_type}")
