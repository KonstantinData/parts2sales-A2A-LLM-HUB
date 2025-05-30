Data Analyst | SQL, Python, Tableau | Machine Learning & Analytics Engineering | Business Process Optimization | Certified Commercial Specialist (IHK)

# PARTS2SALES A2A LLM HUB

## Overview

PARTS2SALES A2A LLM HUB is a modular, agent-driven prompt validation and refinement framework designed for industrial AI prompt pipelines. The central goal of this project is to ensure high-quality prompt development for business-critical applications, particularly in the B2B and manufacturing sector, where structured, interpretable, and reproducible LLM behavior is essential.

This repository supports the development, evaluation, and iterative improvement of prompts using a set of autonomous agents. These agents simulate a feedback loop similar to human-in-the-loop validation but are optimized for automation and scalability.

---

## Project Goals

* **Assure Prompt Quality** : Establish a validation pipeline that assesses prompt effectiveness across dimensions such as task clarity, domain fit, robustness, and composability.
* **Enable Iterative Refinement** : Provide feedback-driven prompt improvement with contextual reasoning, automated explanation, and clear change tracking.
* **Guarantee Reproducibility** : Leverage logs and structured data to trace prompt evolution from version v1 to a validated final template.
* **Support Agent-to-Agent Orchestration (A2A)** : Automate decision-making and task handovers among validation, improvement, and control agents.
* **Provide Scalable Logging & Evaluation** : Use structured feedback logs and visual performance diagnostics to scale prompt QA across multiple templates and tasks.

---

## Agent Architecture

### 1. `PromptQualityAgent`

Responsible for evaluating the prompt using a scoring matrix defined in `config/scoring/quality_scoring_matrix.json` and semantic feedback provided in `config/templates/quality_review_log_template.json`. The evaluation includes weighted dimensions such as:

* Task Clarity
* User Alignment
* Constraint Specification
* Output Structure
* Domain Fit

### 2. `PromptImprovementAgent`

Processes the output of the quality agent and translates suggestions into a refined prompt version. All changes are tracked with an inline rationale for transparency. This agent is intended to eventually rely on GPT (or another LLM) to re-generate the YAML prompt text based on structured feedback.

### 3. `ControllerAgent`

Validates if the improvement made by the `PromptImprovementAgent` aligns with feedback from the `PromptQualityAgent`. If the alignment fails, it initiates a retry loop (max. 3 attempts) and ensures prompt revisions meet the expected quality before proceeding.

### 4. `Execution Phase`

Once a prompt reaches a minimum quality score threshold (e.g., >= 0.85), it is executed with sample data to validate downstream performance (output formatting, extraction consistency, etc.). If successful, the prompt is versioned as `*_template1.yaml`.

---

## Process Flow (A2A Orchestration)

1. A prompt (e.g., `feature_determination_v1.yaml`) is passed to `run_template_batch.py`.
2. `PromptQualityAgent` computes a weighted score and detailed review.
3. If the score is below threshold, `PromptImprovementAgent` refines the prompt.
4. `ControllerAgent` checks if the refinement addressed the original feedback.
5. If not aligned, a retry is triggered (max 3 loops).
6. Once validated, the prompt is saved as final and passed to the execution step.
7. Logs are stored per category: `logs/{quality_log, weighted_score, feedback_log, change_log}`.

This fully agent-driven loop is a blueprint for autonomous prompt QA in industrial-grade prompt systems.

---

## Repository Structure

```
├── agents/                    # Agent definitions (quality, improvement, controller)
├── cli/                       # Entry points (run_template_batch.py)
├── config/
│   ├── scoring/               # Prompt scoring definitions
│   └── templates/             # Human review input templates
├── docs/                      # Visual charts and documentation
├── logs/                      # Evaluation output structured by type
├── prompts/templates/         # Versioned prompt sources (e.g. *_v1.yaml)
├── scripts/                   # Future helpers, execution, preprocessing
└── tests/                     # (Optional) agent test cases and scaffolds
```

---

## Getting Started

```bash
# Set up environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Set your OpenAI API key
echo "OPENAI_API_KEY=sk-..." > .env

# Run for single prompt
python cli/run_template_batch.py --file prompts/templates/feature_determination_v1.yaml

# Or run all registered templates
python cli/run_template_batch.py --all
```

---

## Future Extensions

* Integration with LangChain or CrewAI for dynamic agent orchestration
* Evaluation harness integration (OpenPromptEval, Promptfoo)
* Dataset-driven stress testing and prompt drift monitoring
* Output quality evaluation (e.g., JSON schema conformity)
* GitHub Actions-based CI for prompt regression

---

## Authors

Built with passion by Konstantin Milonas

Data Analyst | SQL, Python, Tableau | Machine Learning & Analytics Engineering | Promt Engineering | Business Process Optimization | Certified Commercial Specialist (IHK)

For questions or contributions, open an issue or contact the maintainer.

---

## License

This project is licensed under a customized [LICENSE ](LICENSE "double click")with additional restrictions.

* ✅ Use allowed for non-commercial, research, and internal applications
* ❌ Commercial use, resale, or model training/fine-tuning on prompt content is prohibited without permission

See [LICENSE ](LICENSE "double click")for details.

© 2025
