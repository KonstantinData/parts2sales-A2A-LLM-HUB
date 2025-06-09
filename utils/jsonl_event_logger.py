"""
utils/jsonl_event_logger.py

Purpose : Appends AgentEvent entries to a workflow-centric JSONL log.
Version : 2.0.0
Author  : Konstantin Milonas with Agentic AI Copilot support
"""

import json
from pathlib import Path
from enum import Enum


class JsonlEventLogger:
    def __init__(self, workflow_id: str, log_dir: Path):
        self.log_path = log_dir / f"{workflow_id}.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event):
        def default(o):
            if isinstance(o, Enum):
                return o.name
            if hasattr(o, "isoformat"):
                return o.isoformat()
            raise TypeError(
                f"Object of type {type(o).__name__} is not JSON serializable"
            )

        # Accept both Pydantic and plain dicts
        if hasattr(event, "model_dump"):
            event_dict = event.model_dump()
        elif hasattr(event, "dict"):
            event_dict = event.dict()
        else:
            event_dict = dict(event)

        with open(self.log_path, "a", encoding="utf-8") as f:
            json_str = json.dumps(event_dict, default=default, ensure_ascii=False)
            json_str = json_str.replace("\n", "")
            f.write(json_str + "\n")
