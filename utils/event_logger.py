"""
event_logger.py

Unified event logging for agentic workflows.
Writes all events as validated AgentEvent JSON.

# Notes:
- Validates AgentEvent before writing.
- Uses naming scheme: {log_dir}/{event_type}/{agent_name}_{timestamp}.json
- Automatically creates needed directories.
"""

from pathlib import Path
import json


def write_event_log(log_dir: Path, event):
    assert hasattr(event, "json"), "Event must be a Pydantic model instance."
    event_type = event.event_type
    agent_name = event.agent_name
    timestamp = event.timestamp.isoformat().replace(":", "-").replace(".", "-")[:19]
    filename = f"{agent_name}_{timestamp}.json"
    path = log_dir / event_type
    path.mkdir(parents=True, exist_ok=True)
    full_path = path / filename

    event_json = json.dumps(
        event.model_dump(), indent=2, ensure_ascii=False, default=str
    )
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(event_json)
    print(f"[LOG] {event_type.upper()} event logged: {full_path.name}")
