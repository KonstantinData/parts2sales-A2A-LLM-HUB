"""
run_prompt_lifecycle.py

Purpose : Main entry point for the full agentic prompt lifecycle.
          Handles evaluation, improvement, versioning, archiving, and
          promotion of prompts across all layers (raw, template, example, production).
Version : 1.1.0
Author  : Konstantin & AI Copilot
Notes   :
- Layer order: 00-raw → 01-templates → 02-example/03-production
- Integrates quality scoring, improvement, controller/approval, and automated archiving
- Scoring matrices and archive paths are injected per layer
- Loads sample data for the template-phase only
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

import pandas as pd

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
THRESHOLD = float(os.getenv("THRESHOLD", "0.90"))
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))
SAMPLE_XLSX = ROOT / "data" / "raw_data" / "mini_stock_list.xlsx"


def parse_version_from_yaml(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("version:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return "0.1.0"


def replace_version_in_yaml(text: str, old: str, new: str) -> str:
    return text.replace(f"version: {old}", f"version: {new}")


def clean_base_name(name: str) -> str:
    for prefix in ["_raw", "_templ", "_config", "_active"]:
        if prefix in name:
            name = name.replace(prefix, "")
    import re

    name = re.sub(r"_v\d+(\.\d+)*$", "", name)
    return name


def _get_scoring_matrix_type(layer: str, agent: str) -> ScoringMatrixType:
    if agent == "quality":
        return ScoringMatrixType.RAW if layer == "raw" else ScoringMatrixType.TEMPLATE
    elif agent == "feature":
        return ScoringMatrixType.FEATURE
    elif agent == "usecase":
        return ScoringMatrixType.USECASE
    elif agent == "industry":
        return ScoringMatrixType.INDUSTRY
    elif agent == "company":
        return ScoringMatrixType.COMPANY
    elif agent == "contact":
        return ScoringMatrixType.CONTACT
    raise ValueError("Unknown agent for scoring matrix type.")


def load_sample_data() -> str:
    if not SAMPLE_XLSX.exists():
        return ""
    df = pd.read_excel(SAMPLE_XLSX)
    # You can convert a sample or the head of the dataframe to a string
    return df.head(3).to_json(orient="records")


def evaluate_and_improve_prompt(prompt_path: Path, layer: str):
    # Quality Agent
    scoring_matrix_type_quality = _get_scoring_matrix_type(layer, "quality")
    quality_agent = PromptQualityAgent(
        scoring_matrix_type=scoring_matrix_type_quality,
        threshold=THRESHOLD,
        openai_client=client,
    )
    # Other agents (static scoring matrix type)
    feature_agent = FeatureExtractionAgent(
        scoring_matrix_type=ScoringMatrixType.FEATURE,
        threshold=THRESHOLD,
        openai_client=client,
    )
    usecase_agent = UsecaseDetectionAgent(
        scoring_matrix_type=ScoringMatrixType.USECASE,
        threshold=THRESHOLD,
        openai_client=client,
    )
    industry_agent = IndustryClassAgent(
        scoring_matrix_type=ScoringMatrixType.INDUSTRY,
        threshold=THRESHOLD,
        openai_client=client,
    )
    company_agent = CompanyMatchAgent(
        scoring_matrix_type=ScoringMatrixType.COMPANY,
        threshold=THRESHOLD,
        openai_client=client,
    )
    contact_agent = ContactMatchAgent(
        scoring_matrix_type=ScoringMatrixType.CONTACT,
        threshold=THRESHOLD,
        openai_client=client,
    )
    improve_agent = PromptImprovementAgent(openai_client=client)
    controller_agent = ControllerAgent(openai_client=client)

    current_path = prompt_path
    raw_base_name = current_path.stem
    semantic_version = parse_version_from_yaml(current_path)
    base_name = clean_base_name(raw_base_name)

    # Prepare sample data if template phase
    sample_data = None
    if layer == "template":
        sample_data = load_sample_data()

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(
            f"🔍 Processing {current_path.name} (iteration {iteration} | version {semantic_version})"
        )
        prompt_text = current_path.read_text(encoding="utf-8")
        meta = {"file": str(current_path)}
        if sample_data:
            meta["sample_data"] = sample_data

        # Evaluate prompt quality (ALWAYS uses LLM now)
        pq_event = quality_agent.run(
            prompt_text,
            base_name,
            iteration,
            prompt_version=semantic_version,
            meta=meta,
        )
        write_event_log(LOG_DIR, pq_event)
        pq_result = pq_event.payload
        score = pq_result.get("score", 0.0)
        pass_threshold = pq_result.get("pass_threshold", False)
        feedback = pq_result.get("feedback", "")

        # Feature extraction (LLM-based)
        feature_event = feature_agent.run(
            prompt_text,
            base_name,
            iteration,
            prompt_version=semantic_version,
            meta=meta,
        )
        write_event_log(LOG_DIR, feature_event)

        # Usecase detection (LLM-based)
        usecase_event = usecase_agent.run(
            prompt_text,
            base_name,
            iteration,
            prompt_version=semantic_version,
            meta=meta,
        )
        write_event_log(LOG_DIR, usecase_event)

        # Industry classification (LLM-based)
        industry_event = industry_agent.run(
            prompt_text,
            base_name,
            iteration,
            prompt_version=semantic_version,
            meta=meta,
        )
        write_event_log(LOG_DIR, industry_event)

        # Company match (LLM-based)
        company_event = company_agent.run(
            prompt_text,
            base_name,
            iteration,
            prompt_version=semantic_version,
            meta=meta,
        )
        write_event_log(LOG_DIR, company_event)

        # Contact match (LLM-based)
        contact_event = contact_agent.run(
            prompt_text,
            base_name,
            iteration,
            prompt_version=semantic_version,
            meta=meta,
        )
        write_event_log(LOG_DIR, contact_event)

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

            if layer == "raw":
                archive_prompt_file(current_path, "00-raw")
            if layer == "template":
                archive_prompt_file(current_path, "01-templates")
            break

        if iteration == MAX_ITERATIONS:
            print("⛔️ Max iterations reached. Aborting.")
            break

        # Improve prompt (always via LLM now)
        imp_event = improve_agent.run(
            prompt_text,
            feedback,
            base_name=base_name,
            iteration=iteration,
            prompt_version=semantic_version,
            meta=meta,
        )
        write_event_log(LOG_DIR, imp_event)

        improved_prompt = imp_event.payload.get("improved_prompt", "")
        rationale = imp_event.payload.get("rationale", "")

        # Version bump for new template version
        next_version = bump(semantic_version, mode="patch")
        improved_prompt = replace_version_in_yaml(
            improved_prompt, semantic_version, next_version
        )
        next_prompt_path = current_path.parent / f"{base_name}_raw_v{next_version}.yaml"
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
