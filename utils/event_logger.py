"""
utils/event_logger.py

Unified event logging for agent workflows.
Writes validated AgentEvent JSONs into logs/{event_type}/
Separately saves pure payload results to data/outputs/

Author: Konstantin & AI Copilot
Version: 1.0.1
"""

from pathlib import Path

BASE_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "outputs"


def write_event_log(event):
    event_type = event.event_type.lower()
    agent_name = event.agent_name
    timestamp = event.timestamp.isoformat().replace(":", "-").replace(".", "-")[:19]

    # Log path per event type
    log_dir = BASE_LOG_DIR / event_type
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{agent_name}_{timestamp}.json"

    # Write full event JSON
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(event.model_dump_json(indent=2))

    print(f"[LOG] {event_type.upper()} event logged: {log_file.name}")

    # Write just payload as separate result file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result_file = OUTPUT_DIR / f"{agent_name}_result_{timestamp}.json"
    with open(result_file, "w", encoding="utf-8") as rf:
        rf.write(
            event.payload.json(indent=2)
            if hasattr(event.payload, "json")
            else str(event.payload)
        )

    print(f"[OUTPUT] Result saved: {result_file.name}")
