"""
run_prompt_lifecycle.py

Purpose : Orchestrates full prompt lifecycle with centralized, workflow-centric JSONL logging.
Version : 1.4.1
Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - All agent events (success & error) are logged in a single workflow JSONL file.
# - Each workflow/session gets a unique workflow_id for full traceability.
# - No more per-agent or per-step logs – just one JSONL log per workflow.
# - Requires all agents to accept and use the workflow_id.
# - Uses improvement_strategy mapping (Enum-based) per layer.
# - Stops early when no version change or score improvement is minimal.
"""

import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.time_utils import cet_now, timestamp_for_filename
import argparse

from utils.openai_client import OpenAIClient
from utils.prompt_versioning import clean_base_name, extract_version
from utils.semantic_versioning_utils import parse_version_from_yaml, bump
from utils.scoring_matrix_types import ScoringMatrixType
from utils.jsonl_event_logger import JsonlEventLogger
from utils.schemas import AgentEvent

from agents.prompt_quality_agent import PromptQualityAgent
from agents.prompt_improvement_agent import PromptImprovementAgent

from utils.improvement_strategies import ImprovementStrategy

# Mapping: layer name -> improvement strategy
improvement_strategy_lookup = {
    "raw": ImprovementStrategy.LLM,
    "template": ImprovementStrategy.LLM,
    "feature_setup": ImprovementStrategy.LLM,
    "usecase_detect": ImprovementStrategy.RULE_BASED,
    "industry_class": ImprovementStrategy.LLM,
    "company_assign": ImprovementStrategy.RULE_BASED,
    "contact_assign": ImprovementStrategy.LLM,
}


def evaluate_and_improve_prompt(
    path: Path, layer: str = "feature_setup", openai_client=None
):
    workflow_id = f"{timestamp_for_filename()}_workflow_{uuid4().hex[:6]}"
    logger = JsonlEventLogger(workflow_id, Path("logs/workflows"))

    iteration = 0
    current_path = path
    prev_score = None
    prev_version = extract_version(current_path.name)

    matrix_lookup = {
        "raw": "RAW",
        "template": "TEMPLATE",
        "feature_setup": "FEATURE",
        "usecase_detect": "USECASE",
        "industry_class": "INDUSTRY",
        "company_assign": "COMPANY",
        "contact_assign": "CONTACT",
    }

    layer_cleaned = layer.lower().lstrip("0123456789_")
    improvement_strategy = improvement_strategy_lookup.get(
        layer_cleaned, ImprovementStrategy.LLM
    )

    while iteration < 7:
        iteration += 1
        current_version = extract_version(current_path.name)
        print(
            f"🔍 Processing {current_path.name} (iteration {iteration} | version {current_version})"
        )

        matrix_name = clean_base_name(current_path.name)
        matrix_key = matrix_lookup.get(matrix_name)

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

        quality_agent = PromptQualityAgent(
            scoring_matrix_type=matrix_type, openai_client=openai_client
        )
        improvement_agent = PromptImprovementAgent(
            improvement_strategy=improvement_strategy, openai_client=openai_client
        )

        pq_event = quality_agent.run(
            current_path,
            base_name=matrix_name,
            iteration=iteration,
            workflow_id=workflow_id,
        )
        logger.log_event(pq_event)

        if pq_event.payload["pass_threshold"]:
            print("✅ Prompt passed quality threshold.")
            break

        score = pq_event.payload.get("score", 0.0)
        if prev_score is not None:
            score_diff = score - prev_score
            if current_version == prev_version or score_diff < 0.01:
                print("⛔️ Early stop: version unchanged or score improvement < 0.01")
                stop_event = AgentEvent(
                    event_type="early_stop",
                    agent_name="LifecycleManager",
                    agent_version="1.0.0",
                    timestamp=cet_now(),
                    step_id="evaluation_loop",
                    prompt_version=current_version,
                    status="stopped",
                    payload={"reason": "no_improvement", "score_diff": score_diff},
                    meta={"iteration": iteration},
                )
                logger.log_event(stop_event)
                break

        prev_score = score
        prev_version = current_version

        improvement_event = improvement_agent.run(
            prompt_path=current_path,
            base_name=matrix_name,
            iteration=iteration,
            workflow_id=workflow_id,
            feedback=pq_event.payload["feedback"],
        )
        logger.log_event(improvement_event)

        old_version = current_version
        new_version = improvement_event.meta.get("new_version") or bump(old_version, "patch")

        print(f"📈 Version bump: {old_version} -> {new_version}")

        if "updated_path" in improvement_event.meta:
            current_path = Path(improvement_event.meta["updated_path"])
        else:
            print("⚠️ No updated_path found in improvement_event.meta. Stopping iteration.")
            break

        if iteration >= 7:
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
