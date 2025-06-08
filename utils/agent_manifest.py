# utils/agent_manifest.py

import yaml
from pathlib import Path
from typing import Dict, Any


class AgentManifest:
    def __init__(self, manifest_path: Path = Path("agents/manifest.yaml")):
        self.manifest_path = manifest_path
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_agent_info(self, agent_name: str) -> Dict[str, Any]:
        return self.manifest.get(agent_name, {})

    def validate_dependency(self, agent_name: str, completed_agents: set) -> bool:
        info = self.get_agent_info(agent_name)
        dependencies = set(info.get("dependencies", []))
        return dependencies.issubset(completed_agents)
