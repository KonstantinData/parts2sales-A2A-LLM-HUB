import os

# Hauptstruktur
folders = [
    "agents/core",
    "agents/extract",
    "agents/reasoning",
    "agents/matchmaking",
    "agents/ops",
    "agents/utils",
    "config/scoring",
    "config",
    "prompts/00-templates",
    "prompts/01-examples",
    "data/inputs",
    "data/outputs",
    "outputs",
    "pipelines",
    "docker",
    "scripts",
    "tests",
    "docs/ADRs",
    "docs/mermaid",
]

files_to_create = {
    "agents/utils/schemas.py": """
from pydantic import BaseModel
from typing import Optional, List, Dict

class Event(BaseModel):
    article: Dict
    features: Optional[Dict]
    use_cases: Optional[Dict]
    industry: Optional[str]
    companies: Optional[List[Dict]]
    meta: Dict
""",
    "agents/utils/llm_judge.py": """
import hashlib, json

def cache_decorator(func):
    _cache = {}
    def wrapper(*args, **kwargs):
        key = hashlib.sha256(json.dumps(args, sort_keys=True, default=str).encode()).hexdigest()
        if key in _cache:
            return _cache[key]
        result = func(*args, **kwargs)
        _cache[key] = result
        return result
    return wrapper

@cache_decorator
def llm_judge(prompt: str) -> float:
    # Hier LLM Call einbauen
    # Dummy: immer 0.95
    return 0.95
""",
    "config/thresholds.yaml": """
prompt_quality: 0.90
feature_quality: 0.90
usecase_quality: 0.90
industry_quality: 0.90
company_quality: 0.90
max_retries: 3
""",
    "pipelines/prefect_flows.py": """
from prefect import flow, task

@task
def ingest_articles(): pass

@task
def build_feature_prompt(): pass

@task
def prompt_quality(): pass

@flow
def main():
    data = ingest_articles()
    prompt = build_feature_prompt()
    score = prompt_quality()
    # usw.

if __name__ == "__main__":
    main()
""",
    "pipelines/run_daily.py": """
import datetime, os
def run_daily():
    today = datetime.date.today().isoformat()
    input_file = f"data/inputs/{today}_articles_raw.jsonl"
    output_dir = f"outputs/{today}/"
    os.makedirs(output_dir, exist_ok=True)
    # Hier: Lade Daten, durchlaufe Pipeline, speichere Outputs
if __name__ == "__main__":
    run_daily()
""",
    "docs/architecture.md": "# Architektur-Überblick\n\nHier folgt die Dokumentation der Agent-Pipeline.",
    "docs/process_flow.md": "# Prozess Flow\n\nHier ist der End-to-End Prozess dokumentiert.",
    "Makefile": """
lint:
\tblack agents/ scripts/ pipelines/

test:
\tpytest tests/

run:
\tpython pipelines/run_daily.py
""",
    "agents/__init__.py": "",
    "agents/core/__init__.py": "",
    "agents/extract/__init__.py": "",
    "agents/reasoning/__init__.py": "",
    "agents/matchmaking/__init__.py": "",
    "agents/ops/__init__.py": "",
    "agents/utils/__init__.py": "",
    "config/scoring/__init__.py": "",
    "tests/__init__.py": "",
    "scripts/__init__.py": "",
    "pipelines/__init__.py": "",
}

for folder in folders:
    os.makedirs(folder, exist_ok=True)

for filename, content in files_to_create.items():
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")

print("Struktur und Startdateien wurden erstellt/ergänzt!")
