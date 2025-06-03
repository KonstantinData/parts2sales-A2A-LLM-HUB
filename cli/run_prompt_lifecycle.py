"""
run_prompt_lifecycle.py

Purpose : Orchestrates full prompt lifecycle: quality scoring, improvement, controller retry. Now uses a centralized OpenAIClient via Dependency Injection for all LLM access.
Version : 1.3.0
Author  : Konstantin’s AI Copilot
Notes   :
- Dynamically detects scoring matrix from prompt filename
- Uses AgentEvent schema + structured JSON logging
- All LLM-based agents receive a single OpenAIClient instance (from utils.openai_client)
- Each agent run logs a versioned output file and controller retry logic
- Supports batch mode via --all
- Now includes unique logging filenames per prompt + iteration
"""

import sys
from pathlib import Path
from datetime import datetime
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.openai_client import OpenAIClient
from utils.prompt_versioning import parse_version_from_yaml, clean_base_name
from utils.event_logger import write_event_log
from utils.scoring_matrix_types import ScoringMatrixType

from agents.prompt_quality_agent import PromptQualityAgent
from agents.prompt_improvement_agent import PromptImprovementAgent
from agents.controller_agent import ControllerAgent


def evaluate_and_improve_prompt(
    path: Path, layer: str = "feature_setup", openai_client=None
):
    base_version = parse_version_from_yaml(path)
    iteration = 0
    current_path = path

    matrix_lookup = {
        "feature_setup": "FEATURE",
        "usecase_detect": "USECASE",
        "industry_class": "INDUSTRY",
        "company_assign": "COMPANY",
        "contact_assign": "CONTACT",
        "template": "TEMPLATE",
        "raw": "RAW",
    }

    while iteration < 3:
        iteration += 1
        print(
            f"🔍 Processing {current_path.name} (iteration {iteration} | version {base_version})"
        )

        matrix_name = clean_base_name(current_path.name)
        matrix_name_cleaned = matrix_name.lower().lstrip("0123456789_")
        matrix_key = matrix_lookup.get(matrix_name_cleaned)
        if not matrix_key:
            raise ValueError(
                f"Unknown or unmapped matrix name '{matrix_name}'. Please update 'matrix_lookup' mapping."
            )
        try:
            matrix_type = ScoringMatrixType[matrix_key]
        except KeyError:
            raise ValueError(
                f"Invalid scoring matrix type: '{matrix_key}'. Available types: {[e.name for e in ScoringMatrixType]}"
            )

        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        quality_agent = PromptQualityAgent(
            scoring_matrix_type=matrix_type, openai_client=openai_client
        )
        pq_event = quality_agent.run(
            current_path, base_name=matrix_name, iteration=iteration
        )
        pq_event.meta["log_id"] = f"{matrix_name}_{iteration}_{timestamp}"
        write_event_log(pq_event)

        if not pq_event.payload["pass_threshold"]:
            improvement_agent = PromptImprovementAgent(openai_client=openai_client)
            pi_event = improvement_agent.run(
                current_path, feedback=pq_event.payload["feedback"]
            )
            write_event_log(pi_event)
            current_path = Path(pi_event.meta["updated_path"])
        else:
            print("✅ Prompt passed quality threshold.")
            break

        controller_agent = ControllerAgent(openai_client=openai_client)
        decision_event = controller_agent.run(pq_event, pi_event)
        write_event_log(decision_event)

        if not decision_event.payload.get("retry", False):
            break

    if iteration >= 3:
        print("⛔️ Max iterations reached. Aborting.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Path to prompt YAML")
    parser.add_argument(
        "--all", action="store_true", help="Evaluate all prompts in prompts/00-raw"
    )
    parser.add_argument("--layer", default="feature_setup", help="Scoring layer name")
    args = parser.parse_args()

    openai_client = OpenAIClient()

    if args.all:
        raw_dir = Path("prompts/00-raw")
        for file in raw_dir.glob("*.yaml"):
            evaluate_and_improve_prompt(file, args.layer, openai_client=openai_client)
    elif args.file:
        evaluate_and_improve_prompt(
            Path(args.file), args.layer, openai_client=openai_client
        )
    else:
        print("⚠️ Please provide either --file or --all")


if __name__ == "__main__":
    main()
