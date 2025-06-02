"""
run_template_batch_latest.py

Purpose : Main runner for agentic, event-driven prompt evaluation workflow.
Version : 1.1.0
Author  : Konstantin’s AI Copilot
Notes   :
- Calls PromptQualityAgent with correct scoring matrix based on layer
- Handles RAW import and stepwise promotion to TEMPLATE/FEATURE/USECASE layer
- Usage: python cli/run_template_batch_latest.py --all or --file <path>
"""

# ... [Import-Section wie gehabt] ...

QUALITY_SCORING_MATRIX_NAME = "raw"  # << Standard auf RAW! Siehe unten für andere Layer


def evaluate_and_improve_prompt(prompt_path: Path, layer="raw"):
    quality_agent = PromptQualityAgent(openai_client=client, scoring_matrix_name=layer)
    # ... [Restlicher Ablauf wie gehabt, Details siehe Ursprungsdatei] ...


def main():
    parser = argparse.ArgumentParser(
        description="Agentic Prompt Template Workflow Runner"
    )
    parser.add_argument("--file", type=str, help="Path to the prompt file")
    parser.add_argument(
        "--all", action="store_true", help="Process all raw prompts in directory"
    )
    parser.add_argument(
        "--layer",
        type=str,
        default="raw",
        help="Scoring matrix to use: raw/template/feature/usecase/industry/contact",
    )
    args = parser.parse_args()

    if args.all:
        if not RAW_DIR.exists():
            print(f"⚠️ Directory {RAW_DIR} not found.")
            return
        for prompt_file in RAW_DIR.glob("*.yaml"):
            evaluate_and_improve_prompt(prompt_file, layer=args.layer)
    elif args.file:
        evaluate_and_improve_prompt(Path(args.file), layer=args.layer)
    else:
        print("⚠️ Please provide either --file <path> or --all.")


if __name__ == "__main__":
    main()
