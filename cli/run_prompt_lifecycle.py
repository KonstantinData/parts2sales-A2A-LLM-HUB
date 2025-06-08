# cli/run_prompt_lifecycle.py

"""
Prompt Lifecycle Runner

Version: 2.0.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Orchestrates full prompt lifecycle with centralized, workflow-centric JSONL logging.
Triggers evaluation, improvement, and re-evaluation using ControllerAgent.
Logs all AgentEvents with workflow_id traceability.
"""

import sys
from pathlib import Path
from uuid import uuid4
import argparse
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.time_utils import timestamp_for_filename, cet_now
from utils.openai_client import OpenAIClient
from agents.controller_agent import ControllerAgent
from utils.schemas import AgentEvent


def write_event_log(events: list[AgentEvent], log_path: Path) -> None:
    with log_path.open("w", encoding="utf-8") as f:
        for event in events:
            f.write(event.model_dump_json() + "\n")


def main():
    parser = argparse.ArgumentParser(description="Run full prompt lifecycle.")
    parser.add_argument(
        "--file", type=str, required=True, help="Path to raw prompt YAML file."
    )
    args = parser.parse_args()

    prompt_path = args.file
    workflow_id = f"{timestamp_for_filename()}_{uuid4().hex[:6]}"

    print(f"🔁 Starting lifecycle for: {prompt_path}")
    print(f"🆔 Workflow ID: {workflow_id}")

    client = OpenAIClient()
    controller = ControllerAgent(client=client, workflow_id=workflow_id)
    events = controller.run(prompt_path)

    log_dir = Path("logs") / "workflow"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{workflow_id}_workflow.jsonl"

    write_event_log(events, log_path)

    print(f"✅ Lifecycle completed. Log written to: {log_path}")


if __name__ == "__main__":
    main()
