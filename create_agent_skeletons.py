import os

AGENT_SKELETONS = {
    # EXTRACT
    "agents/extract/feature_extraction_agent.py": '''
"""
Feature Extraction Agent:
- Extrahiert Features aus Artikeldaten mithilfe eines Prompt-Templates und OpenAI API.
- Prompt-Template wird aus der Config geladen und mit Artikel-Infos gefüllt.
"""

class FeatureExtractionAgent:
    def __init__(self, prompt_template_path="prompts/00-templates/feature_setup_v1.yaml"):
        self.prompt_template_path = prompt_template_path

    def load_template(self):
        with open(self.prompt_template_path, encoding="utf-8") as f:
            return f.read()

    def build_prompt(self, article):
        template = self.load_template()
        return template.format(**article)

    def extract_features(self, article):
        prompt = self.build_prompt(article)
        # Call OpenAI API hier
        raise NotImplementedError("OpenAI API Call hier implementieren.")

''',
    # CORE
    "agents/core/prompt_quality_agent.py": '''
"""
Prompt Quality Agent:
- Bewertet Prompts anhand einer Score-Matrix aus der Config.
- Nutzt LLM oder regelbasierte Scoring-Matrix.
"""

class PromptQualityAgent:
    def __init__(self, scoring_matrix_path="config/scoring/quality_scoring_matrix.json"):
        self.scoring_matrix_path = scoring_matrix_path

    def load_matrix(self):
        import json
        with open(self.scoring_matrix_path, encoding="utf-8") as f:
            return json.load(f)

    def score_prompt(self, prompt_text):
        # TODO: Prompt-Scoring via LLM oder Regelwerk
        raise NotImplementedError("Prompt-Scoring hier implementieren.")

''',
    "agents/core/prompt_improvement_agent.py": '''
"""
Prompt Improvement Agent:
- Optimiert Prompts, die im Quality-Check durchfallen.
- Nutzt LLM oder Heuristik, um Verbesserungsvorschläge zu generieren.
"""

class PromptImprovementAgent:
    def improve_prompt(self, prompt_text, score_feedback):
        # TODO: Prompt-Verbesserung mittels LLM oder Regeln
        raise NotImplementedError("Prompt-Verbesserung hier implementieren.")

''',
    # REASONING
    "agents/reasoning/usecase_detection_agent.py": '''
"""
Use Case Detection Agent:
- Ermittelt Anwendungsfälle für einen Artikel basierend auf Features und Prompt.
"""

class UseCaseDetectionAgent:
    def __init__(self, prompt_template_path="prompts/00-templates/usecase_detect_v1.yaml"):
        self.prompt_template_path = prompt_template_path

    def detect_usecases(self, features, article):
        # TODO: Prompt bauen, LLM aufrufen, Use Cases extrahieren
        raise NotImplementedError("Use Case Detection hier implementieren.")

''',
    "agents/reasoning/industry_class_agent.py": '''
"""
Industry Classification Agent:
- Klassifiziert einen Artikel in die passende Industrie-Klasse (z.B. NAICS) anhand der Use Cases.
"""

class IndustryClassAgent:
    def __init__(self, prompt_template_path="prompts/00-templates/industry_class_v1.yaml"):
        self.prompt_template_path = prompt_template_path

    def classify_industry(self, use_cases, article):
        # TODO: Prompt bauen, LLM aufrufen, Industrie-Klasse bestimmen
        raise NotImplementedError("Industry Classification hier implementieren.")

''',
    # MATCHMAKING
    "agents/matchmaking/company_match_agent.py": '''
"""
Company Match Agent:
- Sucht und scored Firmen (Kundenpotenzial) per Vektor-Suche und LLM-Bewertung.
- Nutzt pgvector oder ähnliche DB für Embeddings.
"""

class CompanyMatchAgent:
    def __init__(self, vector_db_conn_str="postgresql://..."):
        self.vector_db_conn_str = vector_db_conn_str

    def find_candidate_companies(self, industry_code):
        # TODO: pgvector-Query für Top-N Firmen
        raise NotImplementedError("Kandidatensuche hier implementieren.")

    def score_companies(self, candidates, article, features, use_cases):
        # TODO: LLM-Scoring der Kandidaten
        raise NotImplementedError("LLM-Scoring hier implementieren.")

''',
    "agents/matchmaking/crm_sync_agent.py": '''
"""
CRM Sync Agent:
- Synct die Firmenmatches ins CRM (Test-Endpoint oder HubSpot).
- Nutzt das Strategy-Pattern für verschiedene Backends (ENV-gesteuert).
"""

class CRMBackendBase:
    def upsert_companies(self, companies):
        raise NotImplementedError

class LocalTestBackend(CRMBackendBase):
    def upsert_companies(self, companies):
        # TODO: Firmen an lokalen Test-Endpoint senden (z.B. HTTP POST)
        raise NotImplementedError

class HubSpotBackend(CRMBackendBase):
    def upsert_companies(self, companies):
        # TODO: Firmen via HubSpot API batch upsert
        raise NotImplementedError

def get_crm_backend():
    import os
    backend = os.getenv("CRM_BACKEND", "local")
    if backend == "hubspot":
        return HubSpotBackend()
    return LocalTestBackend()

class CRMSyncAgent:
    def __init__(self):
        self.backend = get_crm_backend()
    def sync(self, companies):
        self.backend.upsert_companies(companies)
''',
    # OPS
    "agents/ops/cost_monitor_agent.py": '''
"""
Cost Monitor Agent:
- Liest Token-Nutzung, API-Kosten, Cache-Hitrate und schreibt sie in Log/CloudWatch.
"""

class CostMonitorAgent:
    def __init__(self):
        # TODO: Init für API Usage Monitoring
        pass

    def log_costs(self, usage_data):
        # TODO: Logs oder CloudWatch Metrics schreiben
        raise NotImplementedError("Kostenlogging hier implementieren.")

''',
    # UTILS (optional, falls noch nicht existierend)
    "agents/utils/llm_judge.py": '''
"""
LLM Judge Helper:
- Bewertet beliebige Ergebnisse per LLM-Call, cached via Redis.
"""
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
''',
}

for filepath, code in AGENT_SKELETONS.items():
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code.strip() + "\n")
        print(f"Created {filepath}")
    else:
        print(f"Skipped (exists): {filepath}")

print("Alle Agent-Skeletons sind angelegt!")
