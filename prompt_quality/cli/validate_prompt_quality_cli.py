import os
import argparse
import sys
import json
from datetime import datetime
from colorama import init, Fore, Style

# Projektpfad für Imports sicherstellen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prompt_quality.validators.validate_prompt_quality_en import validate_prompt_en
from prompt_quality.languages import lang_en

init(autoreset=True)

LOG_DIR = os.path.join("prompt_quality", "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def score_validated_row(results: dict) -> float:
    weights = {
        "grammar_check": 0.10,
        "idiomatic_check": 0.05,
        "task_clarity": 0.30,
        "structure_check": 0.25,
        "lexical_fit": 0.10,
        "tone_check": 0.10,
        "translation_integrity": 0.10,
    }
    score = 0.0
    for check, weight in weights.items():
        if results.get(check, {}).get("passed", False):
            score += weight
    return round(score * 20) / 20


def validate_prompt(prompt: str):
    results = validate_prompt_en(prompt)
    explanation_map = lang_en.explanations()
    return results, explanation_map


def log_results(prompt, results, explanation_map, show_score):
    timestamp = datetime.now().strftime("%y%m%d_%I:%M %p")
    log_path = os.path.join(LOG_DIR, f"prompt_check_en_{timestamp}.txt")
    violations = []
    score = 0.0

    with open(log_path, "w", encoding="utf-8") as log:
        log.write(f"Prompt: {prompt}\n\n")
        print(f"\n{Style.BRIGHT}Prompt: {prompt}\n")

        for check, result in results.items():
            passed = result["passed"]
            examples = result.get("examples", [])
            status = f"{Fore.GREEN}✅" if passed else f"{Fore.RED}❌"
            explanation = explanation_map.get(check, "No explanation available.")
            print(f"{check}: {status}")
            log.write(f"{check}: {'PASS' if passed else 'FAIL'}\n")
            if not passed:
                print(f"  → {explanation}")
                log.write(f"  → {explanation}\n")
                for ex in examples:
                    print(f"     ↪ {ex}")
                    log.write(f"     ↪ {ex}\n")
                violations.append(check)

        if show_score:
            score = score_validated_row(results)
            print(f"\n🔢 Score: {score}")
            log.write(f"\nScore: {score}\n")

    return violations, score, timestamp


def json_output(prompt, results):
    violations = [k for k, v in results.items() if not v["passed"]]
    score = score_validated_row(results)
    output = {
        "prompt": prompt,
        "language": "en",
        "score": score,
        "violations": violations,
        "checks": results,
        "timestamp": datetime.now().isoformat(),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Prompt Quality Checker (EN only)")
    parser.add_argument("--prompt", help="Prompt string to validate")
    parser.add_argument("--file", help="Path to prompt file")
    parser.add_argument("--score", action="store_true", help="Display numerical score")
    parser.add_argument(
        "--json", action="store_true", help="Output result in JSON format"
    )
    args = parser.parse_args()

    if args.file:
        from pathlib import Path

        prompt = Path(args.file).read_text(encoding="utf-8")
    else:
        prompt = args.prompt or input("\nEnter the prompt text:\n> ").strip()

    results, explanation_map = validate_prompt(prompt)

    if args.json:
        json_output(prompt, results)
    else:
        log_results(prompt, results, explanation_map, args.score)


if __name__ == "__main__":
    main()
