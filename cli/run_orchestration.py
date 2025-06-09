# cli/run_orchestration.py

import sys
from pathlib import Path
import argparse
from uuid import uuid4
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.time_utils import timestamp_for_filename
from controller.agent_orchestrator import AgentOrchestrator
from utils.pdf_report_generator import generate_pdf_report


def main():
    parser = argparse.ArgumentParser(description="Agent Orchestration Runner")
    parser.add_argument(
        "--sample_file",
        default="data/sample/mini_stock_list.json",
        help="Path to sample input file (e.g. JSON)",
    )
    args = parser.parse_args()

    sample_file = Path(args.sample_file)
    with open("config/max_retries.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    iteration = cfg.get("max_retries", 1)
    base_name = "feature_setup_template_v0.2.0"
    log_dir = Path("logs/workflows")
    workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
    log_path = log_dir / f"{workflow_id}.jsonl"

    # Orchestrator ausführen
    orchestrator = AgentOrchestrator(
        workflow_id=workflow_id,
        sample_file=sample_file,
        log_dir=log_dir,
    )
    final_event = orchestrator.run(
        base_name=base_name,
        iteration=iteration,
    )

    # Nach dem Workflow: PDF-Report erzeugen
    print("🔎 Generating PDF report ...")
    pdf_path = generate_pdf_report(log_path)
    print(f"✅ PDF Report generated: {pdf_path}")

    print(f"Workflow completed. Final event ID: {final_event.event_id}")


if __name__ == "__main__":
    main()
