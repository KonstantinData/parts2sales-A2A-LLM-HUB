# PARTS2SALES A2A LLM HUB

## Overview

**PARTS2SALES A2A LLM HUB** is a modular, agent-driven framework designed to validate and refine prompts within industrial AI pipelines. Tailored for B2B and manufacturing sectors, it ensures the development of high-quality prompts that are structured, interpretable, and reproducible—critical for business applications where consistency and reliability are paramount.

Leveraging autonomous agents, the system simulates a feedback loop akin to human-in-the-loop validation, optimized for automation and scalability. This approach aligns with best practices in prompt engineering, emphasizing precision, relevance, and performance optimization ([promptpanda.io](https://www.promptpanda.io/blog/ai-prompt-validation/?utm_source=chatgpt.com)).

## Key Features

- **Prompt Quality Assurance**: Evaluates prompts across dimensions like task clarity, domain alignment, robustness, and composability.
- **Iterative Refinement**: Provides feedback-driven improvements with contextual reasoning and transparent change tracking.
- **Reproducibility**: Maintains structured logs to trace prompt evolution from initial versions to validated templates.
- **Agent-to-Agent Orchestration (A2A)**: Automates decision-making and task handovers among validation, improvement, and control agents.
- **Scalable Evaluation**: Utilizes structured feedback logs and performance diagnostics to scale prompt quality assurance across multiple templates and tasks.

## Agent Architecture

### 1. `PromptQualityAgent`

Evaluates prompts using a scoring matrix defined in `config/scoring/template_scoring_matrix.py`. Key evaluation dimensions include:
- Task Clarity
- User Alignment
- Constraint Specification
- Output Structure
- Domain Fit

### 2. `PromptImprovementAgent`

Processes feedback from the quality agent to refine prompts. Changes are tracked with inline rationales for transparency. This agent utilizes LLMs to regenerate YAML prompt text based on structured feedback.

### 3. `ControllerAgent`

Validates whether improvements align with feedback from the quality agent. If misalignment is detected, it initiates a retry loop (up to 3 attempts) to ensure prompt revisions meet expected quality standards.

### 4. Execution Phase

Once a prompt achieves a quality score above a defined threshold (e.g., ≥ 0.85), it undergoes execution with sample data to validate downstream performance, including output formatting and extraction consistency. Successful prompts are versioned as `*_template1.yaml`.

## Process Flow (A2A Orchestration)

1. A prompt (e.g., `feature_determination_v1.yaml`) is input into `run_template_batch.py`.
2. `PromptQualityAgent` computes a weighted score and provides a detailed review.
3. If the score is below the threshold, `PromptImprovementAgent` refines the prompt.
4. `ControllerAgent` checks if the refinement addresses the original feedback.
5. If not aligned, a retry is triggered (maximum of 3 loops).
6. Once validated, the prompt is saved as final and proceeds to the execution step.
7. Logs are stored per category: `logs/{quality_log, weighted_score, feedback_log, change_log}`.

This agent-driven loop serves as a blueprint for autonomous prompt quality assurance in industrial-grade systems.

## Repository Structure

```
├── agents/                    # Agent definitions (quality, improvement, controller)
├── cli/                       # Entry points (run_template_batch.py)
├── config/
│   ├── scoring/               # Prompt scoring definitions
│   └── templates/             # Human review input templates
├── docs/                      # Visual charts and documentation
├── logs/                      # Evaluation output structured by type
├── prompts/templates/         # Versioned prompt sources (e.g., *_v1.yaml)
├── scripts/                   # Helper scripts for execution and preprocessing
└── tests/                     # Agent test cases and scaffolds
```

## Getting Started

```bash
# Set up environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set your OpenAI API key
echo "OPENAI_API_KEY=sk-..." > .env

# Run for a single prompt
python cli/run_template_batch.py --file prompts/templates/feature_determination_v1.yaml

# Or run all registered templates
python cli/run_template_batch.py --all
```

## Future Extensions

- **Integration with LangChain or CrewAI**: For dynamic agent orchestration.
- **Evaluation Harness Integration**: Incorporate tools like OpenPromptEval or Promptfoo for enhanced evaluation.
- **Dataset-Driven Stress Testing**: Implement stress tests and monitor prompt drift.
- **Output Quality Evaluation**: Ensure outputs conform to JSON schema standards.
- **CI/CD Integration**: Set up GitHub Actions for prompt regression testing.

## Author

**Konstantin Milonas**  
*Data Analyst | SQL, Python, Tableau | Machine Learning & Analytics Engineering | Prompt Engineering | Business Process Optimization | Certified Commercial Specialist (IHK)*

For inquiries or contributions, please open an issue or contact the maintainer.

## License

This project is licensed under a customized [LICENSE](LICENSE) with the following stipulations:

- ✅ Permitted for non-commercial, research, and internal applications.
- ❌ Commercial use, resale, or model training/fine-tuning on prompt content is prohibited without explicit permission.

See the [LICENSE](LICENSE) file for detailed information.

© 2025
