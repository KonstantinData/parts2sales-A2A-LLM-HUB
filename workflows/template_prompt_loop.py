#!/usr/bin/env python3
"""
File: template_prompt_loop.py
Type: Python Script (Workflow Controller)

Purpose:
--------
This script orchestrates the validation and improvement of YAML prompts using agent components.
It repeatedly validates a prompt using PromptQualityAgent and improves it using PromptImprovementAgent
until a score threshold is reached or the maximum number of iterations is exceeded.

Usage:
------
Called directly from CLI or imported into a CLI handler. Not intended for notebook usage.

Notes:
------
- Requires both agent modules to be functional and OpenAI API key to be available
- Supports flexible prompt versioning (v1, v2, ..., final)
"""

from pathlib import Path
from agents.prompt_quality_agent import PromptQualityAgent
from agents.prompt_improvement_agent import PromptImprovementAgent
import json
import shutil
from datetime import datetime
from utils.time_utils import cet_now


def run_template_loop(
    prompt_path: Path, score_threshold: float = 0.9, max_iterations: int = 3
):
    quality_agent = PromptQualityAgent()
    improve_agent = PromptImprovementAgent()

    version = 1
    base_name = prompt_path.stem.replace("_v1", "")
    parent_dir = prompt_path.parent
    current_path = prompt_path

    while version <= max_iterations:
        print(f"\n--- Iteration v{version} for {current_path.name} ---")

        prompt_text = current_path.read_text(encoding="utf-8")
        score, feedback = quality_agent.run(prompt_text)
        print(f"\n📊 Score: {score}")

        timestamp = cet_now().strftime("%y%m%d_%H%M")
        feedback_path = parent_dir / f"{base_name}_v{version}_feedback_{timestamp}.json"
        feedback_path.write_text(json.dumps(feedback, indent=2, ensure_ascii=False))

        if score >= score_threshold:
            final_path = parent_dir / f"{base_name}_final.yaml"
            shutil.copyfile(current_path, final_path)
            print(f"✅ Score threshold reached. Final saved: {final_path}")
            break

        if version == max_iterations:
            print("⛔️ Max iterations reached. Improvement stopped.")
            break

        # Generate improved prompt
        new_version_path = parent_dir / f"{base_name}_v{version+1}.yaml"
        improved_yaml = improve_agent.run(prompt_text, json.dumps(feedback))
        new_version_path.write_text(improved_yaml)

        current_path = new_version_path
        version += 1
