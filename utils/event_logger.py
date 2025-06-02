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
    assert hasattr(event, "model_dump"), "Event must be a Pydantic model instance."
    event_type = event.event_type
    agent_name = event.agent_name
    timestamp = event.timestamp.isoformat().replace(":", "-").replace(".", "-")[:19]
    filename = f"{agent_name}_{timestamp}.json"
    path = log_dir / event_type
    path.mkdir(parents=True, exist_ok=True)
    full_path = path / filename

    # All datetime fields must be converted to str (isoformat) for JSON
    event_dict = event.model_dump()
    for k, v in event_dict.items():
        if hasattr(v, "isoformat"):
            event_dict[k] = v.isoformat()
    event_json = json.dumps(event_dict, indent=2, ensure_ascii=False)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(event_json)
    print(f"[LOG] {event_type.upper()} event logged: {full_path.name}")
