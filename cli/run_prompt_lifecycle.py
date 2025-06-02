"""
run_prompt_lifecycle.py

Purpose : Main entry point for the full agentic prompt lifecycle.
          Handles evaluation, improvement, versioning, archiving, and
          promotion of prompts across all layers (raw, template, example, production).
Version : 1.1.0
Author  : Konstantin & AI Copilot
Notes   :
- Layer order: 00-raw → 01-templates → 02-example/03-production
- Every scoring and evaluation log is written to logs/weighted_score/ only.
- Calls all relevant agent classes for each prompt, based on file name.
- Enforces _raw_ in all v00-raw filenames, strips _raw_ in every derived version.
- Injects sample data in template-phase.
- Usage:
      python cli/run_prompt_lifecycle.py --all
      python cli/run_prompt_lifecycle.py --file <path>
"""

import os
import sys
import argparse
import shutil
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.prompt_quality_agent import PromptQualityAgent
from agents.prompt_improvement_agent import PromptImprovementAgent
from agents.controller_agent import ControllerAgent
from agents.extract.feature_extraction_agent import FeatureExtractionAgent
from agents.reasoning.usecase_detection_agent import UsecaseDetectionAgent
from agents.reasoning.industry_class_agent import IndustryClassAgent
from agents.matchmaking.company_match_agent import CompanyMatchAgent
from agents.matchmaking.contact_match_agent import ContactMatchAgent
from utils.schema import AgentEvent
from utils.event_logger import write_event_log
from utils.semantic_versioning_utils import bump
from utils.archive_utils import archive_prompt_file
from utils.scoring_matrix_types import ScoringMatrixType

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RAW_DIR = ROOT / "prompts" / "00-raw"
TEMPLATE_DIR = ROOT / "prompts" / "01-templates"
EXAMPLE_DIR = ROOT / "prompts" / "02-examples"
PRODUCTION_DIR = ROOT / "prompts" / "03-production"
LOG_DIR = ROOT / "logs"
SCORE_LOG_DIR = LOG_DIR / "weighted_score"
THRESHOLD = float(os.getenv("THRESHOLD", "0.90"))
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))

AGENT_MAPPING = {
    "feature": FeatureExtractionAgent,
    "usecase": UsecaseDetectionAgent,
    "industry": IndustryClassAgent,
    "company": CompanyMatchAgent,
    "contact": ContactMatchAgent,
}


def parse_version_from_yaml(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("version:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return "0.1.0"


def replace_version_in_yaml(text: str, old: str, new: str) -> str:
    return text.replace(f"version: {old}", f"version: {new}")


def clean_base_name(name: str) -> str:
    # Remove all suffixes and _raw/_templ/_config/_active for clean filenames
    for prefix in ["_raw", "_templ", "_config", "_active"]:
        name = name.replace(prefix, "")
    import re

    name = re.sub(r"_v\d+(\.\d+)*$", "", name)
    return name


def enforce_raw_filename(filename: str) -> str:
    # Ensure '_raw_' is present before version (only for 00-raw layer)
    if "_raw_" not in filename:
        parts = filename.split("_v")
        return f"{parts[0]}_raw_v{parts[1]}"
    return filename


def strip_raw_from_filename(filename: str) -> str:
    # Remove _raw_ from filename
    return filename.replace("_raw_", "_")


def _get_scoring_matrix_type(layer: str) -> ScoringMatrixType:
    if layer == "raw":
        return ScoringMatrixType.RAW
    elif layer == "template":
        return ScoringMatrixType.TEMPLATE
    else:
        raise ValueError(f"Unsupported layer for scoring matrix type: {layer}")


def load_sample_data_for_template():
    sample_data_path = ROOT / "data" / "raw_data" / "mini_stock_list.xlsx"
    if sample_data_path.exists():
        sample_df = pd.read_excel(sample_data_path)
        return sample_df.to_dict(orient="records")
    return None


def run_all_agents(
    prompt_text, base_name, iteration, prompt_version, layer, sample_data
):
    results = {}
    meta = {"sample_data": sample_data} if sample_data else {}
    # Always run PromptQualityAgent first
    quality_agent = PromptQualityAgent(
        scoring_matrix_type=_get_scoring_matrix_type(layer),
        threshold=THRESHOLD,
        openai_client=client,
    )
    pq_event = quality_agent.run(
        prompt_text,
        base_name,
        iteration,
        prompt_version=prompt_version,
        meta=meta,
    )
    write_event_log(SCORE_LOG_DIR, pq_event)
    results["prompt_quality"] = pq_event

    # Run other agents if matching in name
    for key, agent_cls in AGENT_MAPPING.items():
        if key in base_name:
            agent = agent_cls(
                scoring_matrix_type=ScoringMatrixType[key.upper()],
                threshold=THRESHOLD,
                openai_client=client,
            )
            event = agent.run(
                prompt_text,
                base_name,
                iteration,
                prompt_version=prompt_version,
                meta=meta,
            )
            write_event_log(SCORE_LOG_DIR, event)
            results[key] = event
    return results


def evaluate_and_improve_prompt(prompt_path: Path, layer: str):
    current_path = prompt_path
    raw_base_name = current_path.stem
    semantic_version = parse_version_from_yaml(current_path)
    base_name = clean_base_name(raw_base_name)

    # Raw-Datei muss im 00-raw Layer _raw_ enthalten!
    if layer == "raw" and "_raw_" not in raw_base_name:
        correct_name = enforce_raw_filename(raw_base_name)
        corrected_path = current_path.parent / f"{correct_name}.yaml"
        shutil.move(str(current_path), str(corrected_path))
        current_path = corrected_path
        raw_base_name = correct_name

    sample_data = load_sample_data_for_template() if layer == "template" else None

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(
            f"🔍 Processing {current_path.name} (iteration {iteration} | version {semantic_version})"
        )
        prompt_text = current_path.read_text(encoding="utf-8")

        # Run ALL relevant agents and log to weighted_score
        all_results = run_all_agents(
            prompt_text, base_name, iteration, semantic_version, layer, sample_data
        )
        pq_event = all_results["prompt_quality"]
        pq_result = pq_event.payload
        score = pq_result.get("score", 0.0)
        pass_threshold = pq_result.get("pass_threshold", False)
        feedback = pq_result.get("feedback", "")

        if score >= THRESHOLD:
            # Save config version to examples
            config_dir = EXAMPLE_DIR / base_name
            config_dir.mkdir(parents=True, exist_ok=True)
            config_version = "0.3.0"
            config_filename = f"{base_name}_config_v{config_version}.yaml"
            config_path = config_dir / config_filename
            shutil.copyfile(current_path, config_path)
            print(f"✅ Threshold met. Saved config as: {config_path}")

            # Save template version to templates
            template_dir = TEMPLATE_DIR / base_name / f"{base_name}_template"
            template_dir.mkdir(parents=True, exist_ok=True)
            template_version = "1.0.0"
            template_filename = f"{base_name}_template_v{template_version}.yaml"
            template_path = template_dir / template_filename
            template_text = replace_version_in_yaml(
                prompt_text, semantic_version, template_version
            )
            template_path.write_text(template_text, encoding="utf-8")
            print(f"📄 Template saved as: {template_path}")

            # Archive raw after successful template promotion
            if layer == "raw":
                archive_prompt_file(current_path, "00-raw")
            if layer == "template":
                archive_prompt_file(current_path, "01-templates")
            break

        if iteration == MAX_ITERATIONS:
            print("⛔️ Max iterations reached. Aborting.")
            break

        # Improve prompt
        improve_agent = PromptImprovementAgent()
        imp_event = improve_agent.run(
            prompt_text,
            feedback,
            base_name=base_name,
            iteration=iteration,
            prompt_version=semantic_version,
        )
        write_event_log(SCORE_LOG_DIR, imp_event)

        improved_prompt = imp_event.payload.get("improved_prompt", "")
        rationale = imp_event.payload.get("rationale", "")

        # Version bump for new template version
        next_version = bump(semantic_version, mode="patch")
        improved_prompt = replace_version_in_yaml(
            improved_prompt, semantic_version, next_version
        )
        # Remove _raw_ in filename for all improved/template versions!
        parent_dir = current_path.parent
        clean_base = strip_raw_from_filename(base_name)
        next_prompt_path = parent_dir / f"{clean_base}_v{next_version}.yaml"
        next_prompt_path.write_text(improved_prompt, encoding="utf-8")

        # Controller alignment check
        controller_agent = ControllerAgent(openai_client=client)
        ctrl_event = controller_agent.run(
            improved_prompt,
            feedback,
            base_name=clean_base,
            iteration=iteration,
            prompt_version=next_version,
        )
        write_event_log(SCORE_LOG_DIR, ctrl_event)

        action = ctrl_event.payload.get("action", "")
        if action == "retry":
            print("🔄 Controller requests retry.")
            current_path = next_prompt_path
            semantic_version = next_version
            continue
        elif action == "abort":
            print("❌ Controller aborts. No further improvement.")
            break

        current_path = next_prompt_path
        semantic_version = next_version


def main():
    parser = argparse.ArgumentParser(
        description="Agentic Prompt Lifecycle Workflow Runner"
    )
    parser.add_argument("--file", type=str, help="Path to the prompt file")
    parser.add_argument(
        "--all", action="store_true", help="Process all templates in directory"
    )
    parser.add_argument(
        "--layer",
        type=str,
        default="raw",
        choices=["raw", "template"],
        help="Processing layer: raw or template",
    )
    args = parser.parse_args()

    if args.all:
        if args.layer == "raw":
            src_dir = RAW_DIR
        elif args.layer == "template":
            src_dir = TEMPLATE_DIR
        else:
            raise ValueError("Invalid layer")
        if not src_dir.exists():
            print(f"⚠️ Directory {src_dir} not found.")
            return
        for prompt_file in src_dir.glob("**/*.yaml"):
            evaluate_and_improve_prompt(prompt_file, args.layer)
    elif args.file:
        evaluate_and_improve_prompt(Path(args.file), args.layer)
    else:
        print("⚠️ Please provide either --file <path> or --all.")


if __name__ == "__main__":
    main()
