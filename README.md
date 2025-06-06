# PARTS2SALES A2A LLM HUB

## Overview

**PARTS2SALES A2A LLM HUB** is a modular, agent-based prompt lifecycle manager for industrial use cases. The focus is on **fully automated, versioned prompt quality assurance** across all stages: from RAW to PRODUCTION.

The system orchestrates autonomous LLM agents for evaluation, improvement, validation, and archiving of YAML prompts. It ensures traceability, high quality, and maintainability via structured logs, Pydantic schemas, and semantic versioning—**ready for business, AI teams, and CI/CD.**

## Core Features

- **Agentic Prompt Lifecycle:** Automated processing from RAW to PRODUCTION (incl. research loop, scoring, improvement, controller supervision).
- **Strict Versioning:** Complete support for semantic versioning, auto-increment, promotion, patch bump, and archiving.
 - **Flexible Scoring:** Each quality check (raw, template, feature, usecase, industry, company, contact) uses its own scoring matrix (type-safe via Enum). Raw prompts can optionally be scored via the LLM itself by enabling the `use_llm` flag in `LLMPromptScorer`.
- **Pluggable Agents:** Clearly separated, easily extensible agent classes (Quality, Improvement, Controller, Extraction, Matchmaking, Reasoning, Ops).
- **Event Logging & Audit Trail:** Every action, score, or improvement is logged as an AgentEvent in JSON with timestamp and version.
- **Archiving:** Automatic archiving of prompts after every stage transition.
- **.env Config:** No secrets in code, all via OS environment variables.

## Agent Overview

| Agent                  | Purpose/Scope                                       |
| ---------------------- | --------------------------------------------------- |
| PromptQualityAgent     | Rates prompts (scoring, feedback, matrix-based)     |
| PromptImprovementAgent | Improves prompts according to feedback              |
| ControllerAgent        | Supervises, checks compliance, triggers loops/abort |
| FeatureExtractionAgent | Extracts technical features                         |
| CompanyMatchAgent      | Assigns companies to request/context                |
| ContactMatchAgent      | Matches and ranks contacts to companies             |
| CRM Sync Agent         | Synchronizes with HubSpot (or other CRM)            |
| UsecaseDetectionAgent  | Use-case detection, categorization                  |
| IndustryClassAgent     | Industry classification                             |
| CostMonitorAgent       | Monitors token & API costs                          |

## Lifecycle/Process Flow

```mermaid
graph LR
    RAW --> QC[PromptQualityAgent]
    QC -->|score<TH| IMP[PromptImprovementAgent]
    IMP --> QC
    QC -->|score≥TH| CTRL[ControllerAgent]
    CTRL -->|ok| ARCH1[Archive RAW]
    ARCH1 --> TEMPLATE[Promote to Template]
    TEMPLATE --> ARCH2[Archive Template]
    TEMPLATE --> FEATURE[FeatureExtractionAgent] & USECASE[UsecaseDetectionAgent] & INDUSTRY[IndustryClassAgent] & CONTACT[ContactMatchAgent]
    subgraph "Research Loop"
      FEATURE --> QC2
      QC2 -->|score<TH| IMP2
      IMP2 --> QC2
      QC2 -->|score≥TH| CTRL2
      CTRL2 -->|ok| ARCH3
    end
```

**Process (simplified):**

1. CLI runner (`run_prompt_lifecycle.py`) ingests a RAW prompt.
2. Quality check + scoring (via relevant matrix).
3. Loop: Improve/re-evaluate until threshold is met.
4. Controller releases, archives RAW, creates template.
5. Research loop: For each task (feature, usecase, etc.) its own agent/matrix/logic.
6. After each stage: Versioning, logging, archiving.

## Repository Structure

```plaintext
├── agents/
│   ├── base_agent.py
│   ├── prompt_quality_agent.py
│   ├── prompt_improvement_agent.py
│   ├── controller_agent.py
│   ├── extract/feature_extraction_agent.py
│   ├── matchmaking/company_match_agent.py
│   ├── matchmaking/contact_match_agent.py
│   ├── matchmaking/crm_sync_agent.py
│   ├── reasoning/usecase_detection_agent.py
│   ├── reasoning/industry_class_agent.py
│   └── ops/cost_monitor_agent.py
├── cli/
│   └── run_prompt_lifecycle.py
├── config/
│   └── scoring/
│       ├── raw_scoring_matrix.py
│       ├── template_scoring_matrix.py
│       ├── feature_scoring_matrix.py
│       ├── usecase_scoring_matrix.py
│       ├── industry_scoring_matrix.py
│       ├── company_scoring_matrix.py
│       └── contact_scoring_matrix.py
├── utils/
│   ├── event_logger.py
│   ├── scoring_matrix_types.py
│   ├── semantic_versioning_utils.py
│   └── schema.py
├── prompts/
│   ├── 00-raw/
│   ├── 01-templates/
│   ├── 02-examples/
│   └── 99-archive/
├── docs/
├── logs/
└── tests/
```

## .env Template

```env
OPENAI_API_KEY=sk-...
THRESHOLD=0.90
MAX_ITERATIONS=3
HUBSPOT_API_KEY=your-key   # Optional, if CRM sync is enabled
LOG_LEVEL=INFO
USE_LLM_SCORING=true      # Enable LLM-based checks for RAW prompts
```

## Getting Started

```bash
# Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # installs python-dotenv

# Create .env and insert your keys

# RAW → TEMPLATE → RESEARCH → PRODUCTION
python cli/run_prompt_lifecycle.py --all
# ...or for a single file:
python cli/run_prompt_lifecycle.py --file prompts/00-raw/feature_determination.yaml
```

## Advanced

- **Scoring Matrix:** Use via Enum `ScoringMatrixType` (in `utils/scoring_matrix_types.py`), type-checked, customizable per agent.
- **LLM-based scoring:** When `use_llm=True` the quality agent sends prompt and criterion text to OpenAI and interprets the reply as pass/fail (enabled for all prompt stages).
- **Archiving:** Prompts are moved after each status change to `prompts/99-archive/` (with timestamp, stage, version).
- **Test & CI:** All core functions have unit tests, integration tests for the agent pipeline (pytest-ready).

## Author

**Konstantin Milonas & AI Copilot**

## License

See [LICENSE](LICENSE).
Non-commercial, research, and internal use allowed. No resale without permission.

---

© 2025
