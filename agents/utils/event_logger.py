"""
event_logger.py

Unified event logging for agentic workflows.
Writes all events as validated AgentEvent JSON.
"""

from agents.utils.schemas import AgentEvent
from pathlib import Path
import json


def write_event_log(log_dir: Path, event: AgentEvent):
    """
    Writes the event to a JSON file under the correct log directory, using event info for naming.
    #Notes:
    - Validates AgentEvent before writing (raises if invalid).
    - Naming: {log_dir}/{event_type}/{agent_name}_{timestamp}.json
    - Creates directories as needed.
    """
    assert isinstance(event, AgentEvent), "Event must be an AgentEvent instance."
    event_type = event.event_type
    agent_name = event.agent_name
    timestamp = event.timestamp.replace(":", "-").replace(".", "-")[:19]
    filename = f"{agent_name}_{timestamp}.json"
    path = log_dir / event_type
    path.mkdir(parents=True, exist_ok=True)
    full_path = path / filename

    # Pydantic v2+: dict mit model_dump() und dann json.dumps
    event_json = json.dumps(event.model_dump(), indent=2, ensure_ascii=False)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(event_json)
    print(f"[LOG] {event_type.upper()} event logged: {full_path.name}")
