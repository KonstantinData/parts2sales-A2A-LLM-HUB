#!/usr/bin/env python3
"""
File: run_template_batch.py
Type: Python Script (CLI Entry Point)

Purpose:
--------
This script validates and improves a batch of YAML prompt templates located in
`prompts/templates/`, using a multi-step agent workflow.
It evaluates prompt quality, improves them iteratively until a threshold is met,
and writes change logs and versioned files.

Usage:
------
    python run_template_batch.py

Notes:
------
- Outputs logs and improved prompts in the same folder as inputs.
- Prompts must be named *_v1.yaml to follow versioning convention.
"""

from pathlib import Path
from agents.prompt_quality_agent import PromptQualityAgent
from agents.prompt_improvement_agent import PromptImprovementAgent
import json
import shutil
from datetime import datetime

# Configuration
TEMPLATE_DIR = Path("prompts/templates")
PROMPTS = [
    "feature_determination_v1.yaml",
    "use_case_determination_v1.yaml",
    "industry_classification_v1.yaml",
    "company_assignment_v1.yaml",
    "contact_assignment_v1.yaml",
]
THRESHOLD = 0.85
MAX_ITERATIONS = 3


def log_changes(version_path: Path, old_text: str, new_text: str):
    diff_path = version_path.with_suffix("_change_log.txt")
    with diff_path.open("w", encoding="utf-8") as log:
        log.write("# Prompt Change Log\n\n")
        log.write("# Previous Version:\n\n")
        log.write(old_text)
        log.write("\n\n# Improved Version:\n\n")
        log.write(new_text)
    print(f"📝 Change log written to: {diff_path.name}")


def run_batch():
    quality_agent = PromptQualityAgent()
    improve_agent = PromptImprovementAgent()

    for file_name in PROMPTS:
        current_path = TEMPLATE_DIR / file_name
        base_name = current_path.stem.replace("_v1", "")
        version = 1

        while version <= MAX_ITERATIONS:
            print(f"\n🔍 Processing {current_path.name} (v{version})")

            prompt_text = current_path.read_text(encoding="utf-8")
            score, feedback = quality_agent.run(prompt_text)
            print(f"📊 Score: {score}")

            timestamp = datetime.now().strftime("%y%m%d_%H%M")
            feedback_path = current_path.with_name(
                f"{base_name}_v{version}_feedback_{timestamp}.json"
            )
            feedback_path.write_text(json.dumps(feedback, indent=2, ensure_ascii=False))

            if score >= THRESHOLD:
                final_path = TEMPLATE_DIR / f"{base_name}_template1.yaml"
                shutil.copyfile(current_path, final_path)
                print(f"✅ Threshold met. Saved as: {final_path.name}")
                break

            if version == MAX_ITERATIONS:
                print("⛔️ Max iterations reached. Aborting improvement.")
                break

            # Generate improved version
            new_version_path = TEMPLATE_DIR / f"{base_name}_v{version+1}.yaml"
            improved_text = improve_agent.run(prompt_text, json.dumps(feedback))
            new_version_path.write_text(improved_text)
            log_changes(new_version_path, prompt_text, improved_text)

            current_path = new_version_path
            version += 1


if __name__ == "__main__":
    run_batch()
