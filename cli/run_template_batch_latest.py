"""
run_template_batch_latest.py

Main runner for the agentic, event-driven prompt evaluation workflow.
All agents return structured AgentEvent objects. All logs are event logs.
Compatible with OpenAI and future agent plug-and-play.
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# --- Dynamic root import fix ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.prompt_quality_agent import PromptQualityAgent
from agents.prompt_improvement_agent import PromptImprovementAgent
from agents.controller_agent import ControllerAgent
from agents.utils.schemas import AgentEvent
from agents.utils.event_logger import write_event_log
from utils.semantic_versioning_utils import bump

# --- Config ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TEMPLATE_DIR = ROOT / "prompts/00-templates"
EXAMPLE_DIR = ROOT / "prompts/01-examples"
LOG_DIR = ROOT / "logs"
THRESHOLD = float(os.getenv("THRESHOLD", "0.90"))
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))


def parse_version_from_yaml(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("version:"):
            version = line.split(":", 1)[1].strip()
            return version.strip("'\"")
    return "0.1.0"


def replace_version_in_yaml(text: str, old: str, new: str) -> str:
    return text.replace(f"version: {old}", f"version: {new}")


def evaluate_and_improve_prompt(prompt_path: Path):
    quality_agent = PromptQualityAgent(
        openai_client=client, scoring_matrix_name="template"
    )
    improve_agent = PromptImprovementAgent()
    controller_agent = ControllerAgent(client=client)

    current_path = prompt_path
    base_name = current_path.stem.replace("_v1", "")
    semantic_version = parse_version_from_yaml(current_path)
    original_version = semantic_version

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(
            f"🔍 Processing {current_path.name} (iteration {iteration} | version {semantic_version})"
        )
        prompt_text = current_path.read_text(encoding="utf-8")

        # --- Evaluate Quality ---
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

        # --- If threshold met: save versioned example and stop ---
        if score >= THRESHOLD:
            EXAMPLE_DIR.mkdir(parents=True, exist_ok=True)
            final_path = EXAMPLE_DIR / f"{base_name}_example_v{semantic_version}.yaml"
            shutil.copyfile(current_path, final_path)
            print(f"✅ Threshold met. Saved as: {final_path}")
            break

        if iteration == MAX_ITERATIONS:
            print("⛔️ Max iterations reached. Aborting.")
            break

        # --- Improve Prompt ---
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

        # --- Version bump for new template ---
        next_version = bump(semantic_version, mode="patch")
        improved_prompt = replace_version_in_yaml(
            improved_prompt, semantic_version, next_version
        )
        next_prompt_path = TEMPLATE_DIR / f"{base_name}_v{next_version}.yaml"
        next_prompt_path.write_text(improved_prompt)

        # --- Controller Agent: alignment check ---
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

        # --- Next round with improved prompt ---
        current_path = next_prompt_path
        semantic_version = next_version


def main():
    parser = argparse.ArgumentParser(
        description="Agentic Prompt Template Workflow Runner"
    )
    parser.add_argument("--file", type=str, help="Path to the prompt file")
    parser.add_argument(
        "--all", action="store_true", help="Process all templates in directory"
    )
    args = parser.parse_args()

    if args.all:
        if not TEMPLATE_DIR.exists():
            print(f"⚠️ Directory {TEMPLATE_DIR} not found.")
            return
        for prompt_file in TEMPLATE_DIR.glob("*.yaml"):
            evaluate_and_improve_prompt(prompt_file)
    elif args.file:
        evaluate_and_improve_prompt(Path(args.file))
    else:
        print("⚠️ Please provide either --file <path> or --all.")


if __name__ == "__main__":
    main()
