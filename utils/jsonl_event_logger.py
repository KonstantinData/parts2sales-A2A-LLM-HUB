import json
from pathlib import Path
from datetime import datetime
from enum import Enum


class JsonlEventLogger:
    def __init__(self, workflow_id: str, log_dir):
        self.log_path = log_dir / f"{workflow_id}.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event):
        def default(o):
            if isinstance(o, Enum):
                return o.name  # Oder o.value, je nach Wunsch
            if hasattr(o, "isoformat"):
                return o.isoformat()
            raise TypeError(
                f"Object of type {type(o).__name__} is not JSON serializable"
            )

        with open(self.log_path, "a", encoding="utf-8") as f:
            if hasattr(event, "model_dump"):
                event_dict = event.model_dump()
            else:  # pydantic<2
                event_dict = event.dict()
            f.write(json.dumps(event_dict, default=default) + "\n")


"""
# Example inside an agent
from utils.jsonl_event_logger import JsonlEventLogger

logger = JsonlEventLogger(workflow_id="abc123", log_dir=Path("logs/workflows"))
event = AgentEvent(...)  # as usual
logger.log_event(event)

target structure
logs/
  workflows/
    2024-06-03T14-00-00_workflow_abc123.jsonl
    2024-06-03T14-01-30_workflow_def456.jsonl

Convention for workflow_id

Prefer using a UUIDv4, or generate it based on a timestamp combined with user/run context.

Example:
2024-06-03T14-00-00_workflow_abc123.jsonl

Tip:
Put the timestamp at the beginning of the filename to ensure proper sorting.

"""
