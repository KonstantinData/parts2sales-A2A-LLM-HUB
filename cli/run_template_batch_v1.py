# run_template_batch.py
"""
Main batch runner for evaluating and improving YAML prompt templates.

This script supports Semantic Versioning (SemVer) for prompt file versions.
"""

import os
import sys
import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Dynamically add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Agent imports
from agents.prompt_quality_agent import PromptQualityAgent
from agents.prompt_improvement_agent import PromptImprovementAgent
from agents.controller_agent import ControllerAgent

# Configuration
TEMPLATE_DIR = ROOT / "prompts/00-templates"
EXAMPLE_DIR = ROOT / "prompts/01-examples"
LOG_DIR = ROOT / "logs"
THRESHOLD = 0.90
MAX_ITERATIONS = 3
QUALITY_SCORING_MATRIX_PATH = ROOT / "config/scoring/template_scoring_matrix.json"


def parse_version_from_yaml(path: Path) -> str:
    """Extract semantic version from YAML if available."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("version:"):
            return line.split(":", 1)[1].strip()
    return "0.1.0"


def write_log(category: str, name: str, data: dict):
    timestamp = datetime.now().strftime("%y%m%d_%H%M")
    path = LOG_DIR / category / f"{name}_{timestamp}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"📜 {category.upper()} log saved: {path.name}")


def run_template_workflow(prompt_path: Path):
    quality_agent = PromptQualityAgent(
        client, evaluation_path=QUALITY_SCORING_MATRIX_PATH
    )
    improve_agent = PromptImprovementAgent(client, creative_mode=True)

    current_path = prompt_path
    base_name = current_path.stem.replace("_v1", "")
    version = 1
    semantic_version = parse_version_from_yaml(current_path)

    while version <= MAX_ITERATIONS:
        print(f"\n🔍 Processing {current_path.name} (v{version} | {semantic_version})")
        prompt_text = current_path.read_text(encoding="utf-8")

        score, feedback = quality_agent.run(prompt_text, base_name, version)
        write_log("prompt_log", f"{base_name}_v{version}", {"content": prompt_text})
        write_log("quality_log", f"{base_name}_v{version}", feedback)
        write_log("weighted_score", f"{base_name}_v{version}", {"score": score})

        if score >= THRESHOLD:
            EXAMPLE_DIR.mkdir(parents=True, exist_ok=True)
            final_path = EXAMPLE_DIR / f"{base_name}_example_v{semantic_version}.yaml"
            shutil.copyfile(current_path, final_path)
            print(f"✅ Threshold met. Saved as: {final_path}")
            break

        if version == MAX_ITERATIONS:
            print("⛔️ Max iterations reached. Aborting.")
            break

        improved_text, rationale = improve_agent.run(prompt_text, feedback)
        next_version = version + 1
        next_prompt_path = TEMPLATE_DIR / f"{base_name}_v{next_version}.yaml"
        next_prompt_path.write_text(improved_text)

        write_log(
            "prompt_log", f"{base_name}_v{next_version}", {"content": improved_text}
        )
        write_log("feedback_log", f"{base_name}_v{next_version}", feedback)
        write_log(
            "change_log",
            f"{base_name}_v{version}_to_v{next_version}",
            {
                "version_from": f"v{version}",
                "version_to": f"v{next_version}",
                "timestamp": datetime.now().isoformat(),
                "diff_text": {"before": prompt_text, "after": improved_text},
                "rationale": rationale,
            },
        )

        controller = ControllerAgent(base_name, version, LOG_DIR, client)
        if not controller.check_alignment(improved_text, feedback):
            if controller.request_retry():
                time.sleep(1)
                continue
            else:
                print("❌ Retry failed or limit reached. Aborting.")
                break

        current_path = next_prompt_path
        version += 1
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="Prompt Template Evaluator & Improver")
    parser.add_argument("--file", type=str, help="Path to the prompt file")
    parser.add_argument(
        "--all", action="store_true", help="Check all predefined templates"
    )
    args = parser.parse_args()

    if args.all:
        if not TEMPLATE_DIR.exists():
            print(f"⚠️ Directory {TEMPLATE_DIR} not found.")
            return
        for prompt_file in TEMPLATE_DIR.glob("*.yaml"):
            run_template_workflow(prompt_file)
    elif args.file:
        run_template_workflow(Path(args.file))
    else:
        print("⚠️ Please provide either --file <path> or --all.")


if __name__ == "__main__":
    main()
