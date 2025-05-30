#!/usr/bin/env python3
"""
File: run_template_batch.py
Type: Python Script (CLI Entry Point)

Purpose:
--------
This script validates and improves one or multiple YAML prompt templates using a CLI interface.
It evaluates prompt quality, improves them iteratively until a threshold is met,
and writes structured feedback and change logs in JSON format.

Usage:
------
    python run_template_batch.py --file prompts/templates/feature_determination_v1.yaml
    python run_template_batch.py --all

Notes:
------
- Outputs logs and improved prompts in the structured logs/ directory.
- Prompts must be named *_v1.yaml to follow versioning convention.
"""

import sys
from pathlib import Path
import argparse
import json
import shutil
from datetime import datetime

from agents.prompt_quality_agent import PromptQualityAgent
from agents.prompt_improvement_agent import PromptImprovementAgent
from controller_agent import ControllerAgent

# Ensure root project directory is in PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Configuration
TEMPLATE_DIR = Path("prompts/templates")
LOG_DIR = Path("logs")
THRESHOLD = 0.85
MAX_ITERATIONS = 5


def write_log(category: str, name: str, data: dict):
    path = LOG_DIR / category / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"📝 {category.upper()} log saved: {path.name}")


def run_template_workflow(prompt_path: Path):
    quality_agent = PromptQualityAgent()
    improve_agent = PromptImprovementAgent()

    current_path = prompt_path
    base_name = current_path.stem.replace("_v1", "")
    version = 1

    while version <= MAX_ITERATIONS:
        print(f"\n🔍 Processing {current_path.name} (v{version})")
        prompt_text = current_path.read_text(encoding="utf-8")

        # Score & evaluate
        score, feedback = quality_agent.run(prompt_text)
        write_log("quality_log", f"{base_name}_v{version}", feedback)
        write_log("weighted_score", f"{base_name}_v{version}", {"score": score})

        if score >= THRESHOLD:
            final_path = TEMPLATE_DIR / f"{base_name}_template1.yaml"
            shutil.copyfile(current_path, final_path)
            print(f"✅ Threshold met. Saved as: {final_path.name}")
            break

        if version == MAX_ITERATIONS:
            print("⛔️ Max iterations reached. Aborting.")
            break

        # Improvement Phase
        improved_text = improve_agent.run(prompt_text, json.dumps(feedback))
        next_version = version + 1
        next_prompt_path = TEMPLATE_DIR / f"{base_name}_v{next_version}.yaml"
        next_prompt_path.write_text(improved_text)

        write_log("feedback_log", f"{base_name}_v{next_version}", feedback)
        write_log(
            "change_log",
            f"{base_name}_v{version}_to_v{next_version}",
            {
                "version_from": f"v{version}",
                "version_to": f"v{next_version}",
                "timestamp": datetime.now().isoformat(),
                "diff_text": {"before": prompt_text, "after": improved_text},
                "rationale": "Improved via GPT based on feedback",
            },
        )

        # Controller check
        controller = ControllerAgent(base_name, version, LOG_DIR)
        if not controller.check_alignment():
            if controller.request_retry():
                continue
            else:
                print("❌ Retry failed or limit reached. Aborting.")
                break

        current_path = next_prompt_path
        version += 1


def main():
    parser = argparse.ArgumentParser(description="Prompt Template Validator & Improver")
    parser.add_argument("--file", type=str, help="Path to the prompt file")
    parser.add_argument(
        "--all", action="store_true", help="Check all templates sequentially"
    )
    args = parser.parse_args()

    if args.all:
        prompts = [
            "feature_determination_v1.yaml",
            "use_case_determination_v1.yaml",
            "industry_classification_v1.yaml",
            "company_assignment_v1.yaml",
            "contact_assignment_v1.yaml",
        ]
        for prompt_file in prompts:
            run_template_workflow(TEMPLATE_DIR / prompt_file)
    elif args.file:
        run_template_workflow(Path(args.file))
    else:
        print("⚠️ Please provide either --file or --all.")


if __name__ == "__main__":
    main()
