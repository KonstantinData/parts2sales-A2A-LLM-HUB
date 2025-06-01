import os
import yaml
from prompt_quality.cli.validate_prompt_quality_cli import (
    validate_prompt,
    log_results,
)

TEMPLATE_DIR = "prompts/00-templates"


def run_template_validation():
    for filename in os.listdir(TEMPLATE_DIR):
        if filename.endswith("template.yaml"):
            filepath = os.path.join(TEMPLATE_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                role = data.get("role", "")
                objective = data.get("objective", "")
                constraints = data.get("constraints", [])
                prompt = (
                    f"{role.strip()}\n\n{objective.strip()}\n\nConstraints:\n- "
                    + "\n- ".join(constraints)
                )

                if not prompt.strip():
                    print(f"⚠️ No 'prompt' could be constructed in {filename}")
                    continue

                language = "en"  # Statt detect_language()
                results, explanation_map = validate_prompt(prompt, language)
                log_results(prompt, language, results, explanation_map, show_score=True)


if __name__ == "__main__":
    print("🔍 Validating prompt in template.yaml...")
    run_template_validation()
