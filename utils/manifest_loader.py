# utils/manifest_loader.py

from pathlib import Path
import yaml
from typing import Dict, Any


class AgentManifest:
    def __init__(self, manifest_path: Path = Path("agents/manifest.yaml")):
        self.manifest_path = manifest_path
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_agent_metadata(self, agent_name: str) -> Dict[str, Any]:
        return self.manifest.get(agent_name, {})

    def get_dependencies(self, agent_name: str) -> list[str]:
        return self.manifest.get(agent_name, {}).get("dependencies", [])

    def validate_dependency_chain(self, agent_name: str, executed: set[str]) -> bool:
        required = set(self.get_dependencies(agent_name))
        return required.issubset(executed)
