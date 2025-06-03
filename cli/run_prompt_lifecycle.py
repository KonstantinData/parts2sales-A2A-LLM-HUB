"""
run_prompt_lifecycle.py

Purpose : Orchestrates full prompt lifecycle: quality scoring, improvement, controller retry.
Version : 1.2.6
Author  : Konstantin’s AI Copilot
Notes   :
- Dynamically detects scoring matrix from prompt filename
- Uses AgentEvent schema + structured JSON logging
- Each agent run logs a versioned output file and controller retry logic
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
from utils.prompt_versioning import parse_version_from_yaml, clean_base_name
from utils.event_logger import write_event_log
from utils.scoring_matrix_types import ScoringMatrixType

from agents.prompt_quality_agent import PromptQualityAgent
from agents.prompt_improvement_agent import PromptImprovementAgent
from agents.controller_agent import ControllerAgent


def evaluate_and_improve_prompt(path: Path, layer: str = "feature_setup"):
    base_version = parse_version_from_yaml(path)
    iteration = 0
    current_path = path

    while iteration < 3:
        iteration += 1
        print(
            f"🔍 Processing {current_path.name} (iteration {iteration} | version {base_version})"
        )

        matrix_name = clean_base_name(current_path.name)

        # Normalize matrix_name by stripping leading numerics and underscores
        matrix_name_cleaned = "".join(filter(str.isalpha, matrix_name.lower()))

        matrix_lookup = {
            "featuresetup": "FEATURE",
            "usecasesetup": "USECASE",
            "industrysetup": "INDUSTRY",
            "companysetup": "COMPANY",
            "contactsetup": "CONTACT",
            "template": "TEMPLATE",
            "raw": "RAW",
        }

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

        quality_agent = PromptQualityAgent(scoring_matrix_type=matrix_type)
        pq_event = quality_agent.run(
            current_path, base_name=matrix_name, iteration=iteration
        )
        write_event_log(pq_event)

        if not pq_event.payload["pass_threshold"]:
            improvement_agent = PromptImprovementAgent()
            pi_event = improvement_agent.run(
                current_path, feedback=pq_event.payload["feedback"]
            )
            write_event_log(pi_event)
            current_path = pi_event.meta["updated_path"]
        else:
            print("✅ Prompt passed quality threshold.")
            break

        controller_agent = ControllerAgent()
        decision_event = controller_agent.run(pq_event, pi_event)
        write_event_log(decision_event)

        if not decision_event.payload.get("retry", False):
            break

    if iteration >= 3:
        print("⛔️ Max iterations reached. Aborting.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to prompt YAML")
    parser.add_argument("--layer", default="feature_setup", help="Scoring layer name")
    args = parser.parse_args()

    evaluate_and_improve_prompt(Path(args.file), args.layer)


if __name__ == "__main__":
    main()
