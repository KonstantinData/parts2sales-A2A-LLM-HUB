# run_template_batch.py
"""
CLI Runner for Agent-Based Prompt Evaluation and Improvement

Purpose:
--------
This script orchestrates:
- Quality scoring via PromptQualityAgent
- Iterative prompt improvements via PromptImprovementAgent
- Feedback validation via ControllerAgent

It supports both single-file mode (--file) and batch mode (--all).

#Notes:
- Uses JSON logs per version in /logs/{quality|feedback|change}_log/
- Prompts must follow *_v1.yaml versioning for correct iteration
"""

import sys
from pathlib import Path
import argparse
import json
import shutil
from datetime import datetime

# Agent imports
from agents.prompt_quality_agent import PromptQualityAgent
from agents.prompt_improvement_agent import PromptImprovementAgent
from controller_agent import ControllerAgent

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

        # Step 1: Evaluate quality
        score, feedback = quality_agent.run(prompt_text, base_name, version)
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

        # Step 2: Improve prompt
        improved_text, rationale = improve_agent.run(prompt_text, feedback)
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
                "rationale": rationale,
            },
        )

        # Step 3: Alignment check
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
    parser = argparse.ArgumentParser(description="Prompt Template Evaluator & Improver")
    parser.add_argument("--file", type=str, help="Path to the prompt file")
    parser.add_argument(
        "--all", action="store_true", help="Check all predefined templates"
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
        print("⚠️ Please provide either --file <path> or --all.")


if __name__ == "__main__":
    main()
