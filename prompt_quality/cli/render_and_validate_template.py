# test\_prompt\_quality\_usecase.py

# --------------------------------------

# Purpose:

# Unit test to verify that a given prompt template for use case extraction

# passes all defined quality checks in English.

# Goals:

# - Ensure prompt templates conform to quality standards

# - Enable automatic CI checks for regression prevention

# Use Cases:

# - Part of pre-merge checks in CI pipelines

# - Local test validation for prompt authors

from prompt\_quality.validate\_prompt\_quality\_en import validate\_prompt\_en
import json

# Test quality of a use case extraction template prompt

# -----------------------------------------------------

def test\_usecase\_extraction\_quality():
with open("prompts/templates/usecase\_extraction.template.json") as f:
template = json.load(f)

```
# Assumes the 'instruction' field contains the prompt body
prompt_text = template["instruction"]
result = validate_prompt_en(prompt_text)

# All checks must pass
for check, passed in result.items():
    assert passed, f"Prompt failed on: {check}"
```

# render\_and\_validate\_template.py

# ------------------------------------------

# Purpose:

# Combine a JSON-based prompt template with sample input and validate

# the filled result for linguistic quality.

# Goals:

# - Simulate template use with realistic data

# - Evaluate prompt using language-specific validation

# - Output prompt and quality results to terminal and log

# Use Cases:

# - Manual inspection and QA of prompt templates

# - Developer-facing CLI before PR submission

import json
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(**file**), "..")))

from prompt\_quality.validate\_prompt\_quality\_en import validate\_prompt\_en
from prompt\_quality.validate\_prompt\_quality\_de import validate\_prompt\_de
from prompt\_quality import lang\_en
from prompt\_quality import lang\_de

LOG\_DIR = "prompt\_quality/logs"
os.makedirs(LOG\_DIR, exist\_ok=True)

# Replace {{placeholders}} in the template with real values

# ----------------------------------------------------------

def fill\_placeholders(template\_text: str, values: dict) -> str:
for key, val in values.items():
template\_text = re.sub(f"{{{{{key}}}}}", val, template\_text)
return template\_text

# Construct full prompt string from its components

# -----------------------------------------------

def combine\_prompt(data: dict) -> str:
role = data.get("role", "")
objective = data.get("objective", "")
instruction = data.get("instruction", "")
return "\n".join(
filter(None, \[role, f"Objective: {objective}" if objective else None, instruction])
)

# CLI-based prompt template renderer and validator

# ------------------------------------------------

def main():
template\_path = input("Path to template .json: ").strip()
example\_path = os.path.join("prompts", "examples", "testing\_sample.json")
print(f"Using default example: {example\_path}")

```
language = input("Language (en/de): ").strip().lower()

with open(template_path, "r", encoding="utf-8") as f:
    template_data = json.load(f)

with open(example_path, "r", encoding="utf-8") as f:
    example_data = json.load(f)

if isinstance(example_data, list):
    example_data = example_data[0]

full_prompt = combine_prompt(template_data)
input_filled = fill_placeholders(json.dumps(template_data.get("input", {})), example_data)
full_prompt_with_input = full_prompt + "\n\nProduct:\n" + input_filled

if language == "en":
    results = validate_prompt_en(full_prompt_with_input)
    explanations = lang_en.explanations()
else:
    results = validate_prompt_de(full_prompt_with_input)
    explanations = lang_de.explanations()

print("\nPrompt Preview:\n----------------")
print(full_prompt_with_input)

print("\nQuality Checks:\n----------------")
timestamp = datetime.now().strftime("%Y-%m-%dT%H_%M_%S")
log_path = os.path.join(LOG_DIR, f"prompt_check_{language}_{timestamp}.txt")

with open(log_path, "w", encoding="utf-8") as log:
    log.write(f"Prompt: {full_prompt_with_input}\n\n")
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        explanation = explanations.get(check, "No explanation available.")
        print(f"{check}: {status}")
        if not passed:
            print(f"  → {explanation}")
        log.write(f"{check}: {status}\n")
        if not passed:
            log.write(f"  → {explanation}\n")
```

if **name** == "**main**":
main()
