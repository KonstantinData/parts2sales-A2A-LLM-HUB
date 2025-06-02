"""
run_prompt_lifecycle.py

Purpose : Main entry point for the full agentic prompt lifecycle.
          Handles evaluation, improvement, versioning, archiving, and
          promotion of prompts across all layers (raw, template, example, production).
Version : 1.0.0
Author  : Konstantin’s AI Copilot
Notes   :
- Layer order: 00-raw → 01-templates → 02-example/03-production
- Integrates quality scoring, improvement, controller/approval, and automated archiving
- Scoring matrices and archive paths are injected per layer
- Usage:
      python cli/run_prompt_lifecycle.py --all
      python cli/run_prompt_lifecycle.py --file <path>
"""

import os
import sys
import argparse
import shutil
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
from agents.utils.schemas import AgentEvent
from agents.utils.event_logger import write_event_log
from utils.semantic_versioning_utils import bump
from utils.archive_utils import archive_prompt_file

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RAW_DIR = ROOT / "prompts" / "00-raw"
TEMPLATE_DIR = ROOT / "prompts" / "01-templates"
EXAMPLE_DIR = ROOT / "prompts" / "02-examples"
PRODUCTION_DIR = ROOT / "prompts" / "03-production"
LOG_DIR = ROOT / "logs"
THRESHOLD = float(os.getenv("THRESHOLD", "0.90"))
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))
QUALITY_SCORING_MATRIX_NAME = "raw"  # default for raw evaluation


def parse_version_from_yaml(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("version:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return "0.1.0"


def replace_version_in_yaml(text: str, old: str, new: str) -> str:
    return text.replace(f"version: {old}", f"version: {new}")


def clean_base_name(name: str) -> str:
    """
    Remove known prefixes like 'raw_' or version suffixes from the base name to
    get the process name for correct naming.
    """
    for prefix in ["_raw", "_templ", "_config", "_active"]:
        if prefix in name:
            name = name.replace(prefix, "")
    import re

    name = re.sub(r"_v\d+(\.\d+)*$", "", name)
    return name


def evaluate_and_improve_prompt(prompt_path: Path, layer: str):
    quality_agent = PromptQualityAgent(
        openai_client=client,
        scoring_matrix_name=(
            QUALITY_SCORING_MATRIX_NAME
            if layer == "raw"
            else clean_base_name(prompt_path.stem)
        ),
    )
    improve_agent = PromptImprovementAgent()
    controller_agent = ControllerAgent(client=client)

    current_path = prompt_path
    raw_base_name = current_path.stem
    semantic_version = parse_version_from_yaml(current_path)
    base_name = clean_base_name(raw_base_name)

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(
            f"🔍 Processing {current_path.name} (iteration {iteration} | version {semantic_version})"
        )
        prompt_text = current_path.read_text(encoding="utf-8")

        # Evaluate prompt quality
        pq_event = quality_agent.run(
            prompt_text,
            base_name,
            iteration,
            prompt_version=semantic_version,
            meta={"file": str(current_path)},
        )
        write_event_log(LOG_DIR, pq_event)
        pq_result = pq_event.payload
        score = pq_result.get("score", 0.0)
        pass_threshold = pq_result.get("pass_threshold", False)
        feedback = pq_result.get("feedback", "")

        if score >= THRESHOLD:
            # Save config version to examples
            config_dir = EXAMPLE_DIR / base_name
            config_dir.mkdir(parents=True, exist_ok=True)
            config_version = "0.3.0"  # Fixed config version per lab conventions
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
            # Archive template after example/production
            if layer == "template":
                archive_prompt_file(current_path, "01-templates")
            break

        if iteration == MAX_ITERATIONS:
            print("⛔️ Max iterations reached. Aborting.")
            break

        # Improve prompt
        imp_event = improve_agent.run(
            prompt_text,
            feedback,
            base_name=base_name,
            iteration=iteration,
            prompt_version=semantic_version,
        )
        write_event_log(LOG_DIR, imp_event)

        improved_prompt = imp_event.payload.get("improved_prompt", "")
        rationale = imp_event.payload.get("rationale", "")

        # Version bump for new template version
        next_version = bump(semantic_version, mode="patch")
        improved_prompt = replace_version_in_yaml(
            improved_prompt, semantic_version, next_version
        )
        next_prompt_path = current_path.parent / f"{base_name}_v{next_version}.yaml"
        next_prompt_path.write_text(improved_prompt, encoding="utf-8")

        # Controller alignment check
        ctrl_event = controller_agent.run(
            improved_prompt,
            feedback,
            base_name=base_name,
            iteration=iteration,
            prompt_version=next_version,
        )
        write_event_log(LOG_DIR, ctrl_event)

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
