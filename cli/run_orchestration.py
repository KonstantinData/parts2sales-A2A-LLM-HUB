# cli/run_orchestration.py

import sys
from pathlib import Path
import argparse
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.time_utils import timestamp_for_filename
from controller.agent_orchestrator import AgentOrchestrator
from utils.pdf_report_generator import generate_pdf_report


def main():
    parser = argparse.ArgumentParser(description="Agent Orchestration Runner")
    parser.add_argument(
        "--sample_file", required=True, help="Path to sample input file (e.g. JSON)"
    )
    parser.add_argument("--base_name", required=True, help="Base prompt name")
    parser.add_argument("--iteration", type=int, default=1, help="Iteration index")
    parser.add_argument(
        "--log_dir", default="logs/workflows", help="Workflow log storage directory"
    )
    args = parser.parse_args()

    sample_file = Path(args.sample_file)
    base_name = args.base_name
    iteration = args.iteration
    log_dir = Path(args.log_dir)
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
