# utils/jsonl_event_logger.py

from pathlib import Path


class JsonlEventLogger:
    def __init__(self, workflow_id: str, log_dir: Path):
        self.logfile = log_dir / f"{workflow_id}.jsonl"
        self.logfile.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event):
        """Append event (as dict or Pydantic model) to the workflow JSONL file."""
        import json

        with open(self.logfile, "a", encoding="utf-8") as f:
            if hasattr(event, "model_dump"):
                f.write(json.dumps(event.model_dump()) + "\n")
            else:
                f.write(json.dumps(event) + "\n")


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
