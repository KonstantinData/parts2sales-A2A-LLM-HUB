"""
CRM Sync Agent:
- Synct die Firmenmatches ins CRM (Test-Endpoint oder HubSpot).
- Nutzt das Strategy-Pattern für verschiedene Backends (ENV-gesteuert).
"""

class CRMBackendBase:
    def upsert_companies(self, companies):
        raise NotImplementedError

class LocalTestBackend(CRMBackendBase):
    def upsert_companies(self, companies):
        # TODO: Firmen an lokalen Test-Endpoint senden (z.B. HTTP POST)
        raise NotImplementedError

class HubSpotBackend(CRMBackendBase):
    def upsert_companies(self, companies):
        # TODO: Firmen via HubSpot API batch upsert
        raise NotImplementedError

def get_crm_backend():
    import os
    backend = os.getenv("CRM_BACKEND", "local")
    if backend == "hubspot":
        return HubSpotBackend()
    return LocalTestBackend()

class CRMSyncAgent:
    def __init__(self):
        self.backend = get_crm_backend()
    def sync(self, companies):
        self.backend.upsert_companies(companies)
