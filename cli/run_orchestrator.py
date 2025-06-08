# cli/run_orchestration.py

"""
run_orchestration.py

Purpose : CLI entrypoint to run full agent orchestration pipeline from raw input to evaluation.
Version : 2.0.0
Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Uses controller.agent_orchestrator.AgentOrchestrator
# - Accepts input file path and base name for prompt versioning
"""

import argparse
from pathlib import Path
from controller.agent_orchestrator import AgentOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Run full orchestration pipeline.")
    parser.add_argument("--file", required=True, help="Path to input file")
    parser.add_argument("--base", required=True, help="Prompt version base name")
    parser.add_argument(
        "--iteration", type=int, default=1, help="Iteration number (default: 1)"
    )
    args = parser.parse_args()

    input_path = Path(args.file)
    base_name = args.base
    iteration = args.iteration

    orchestrator = AgentOrchestrator()
    orchestrator.run(input_path=input_path, base_name=base_name, iteration=iteration)


if __name__ == "__main__":
    main()
