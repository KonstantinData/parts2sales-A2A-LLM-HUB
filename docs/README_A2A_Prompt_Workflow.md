# A2A Prompt Engineering Workflow

## Project Structure

├── 00-templates/             # Raw structured prompt blueprints (multiple layers by feature)

├── 01-examples/              # Evaluation-ready drafts/templates from raw files

├── 02-production/            # Validated and system-integrated production prompts

├── config/                   # Configuration files for scoring matrices and parameters

├── logs/                     # All generated logs (prompt, quality, feedback, etc.)

├── prompts/                  # Entry point folder for structured YAML prompts

├── cli/                      # CLI scripts to automate workflows

└── agents/                   # Agent implementations and core logic


## Naming Convention & Semantic Versioning

All prompt files follow this strict semantic versioning and suffix convention for clarity, traceability, and staging:

| Stage    | Filename Pattern         | Meaning                       |
| -------- | ------------------------ | ----------------------------- |
| Raw      | `*_raw_vX.Y.Z.yaml`    | Untested structural base      |
| Template | `*_templ_vX.Y.Z.yaml`  | Formatted and draft-ready     |
| Config   | `*_config_vX.Y.Z.yaml` | Tested and refined in lab     |
| Active   | `*_active_vX.Y.Z.yaml` | Production ready and deployed |

### Versioning

The `version:` field inside YAML prompts and filenames uses semantic versioning:

| Version | Meaning                           |
| ------- | --------------------------------- |
| 0.x.y   | Experimental or beta phase        |
| 1.0.0   | First stable production release   |
| 1.x.y   | Backwards-compatible feature/fix  |
| 2.0.0   | Major redesign / breaking changes |

### Examples

| Use Case                | Example Filename                      |
| ----------------------- | ------------------------------------- |
| Company assignment      | `company_assign_raw_v0.1.0.yaml`    |
| Contact assignment      | `contact_assign_templ_v0.2.0.yaml`  |
| Feature setup           | `feature_setup_active_v1.0.0.yaml`  |
| Industry classification | `industry_class_config_v0.3.0.yaml` |
| Use case detection      | `usecase_detect_active_v1.0.0.yaml` |

## Workflow Description

This prompt development workflow supports iterative evaluation and improvement with clear audit trails:

1. **Start with a Raw prompt file** (`*_raw_vX.Y.Z.yaml`)
2. **Log initial prompt state**
3. **Run `PromptQualityAgent` to evaluate prompt quality**
4. **Write quality and score logs**
5. **Evaluate if score meets the threshold**
   - If the OpenAI API is unavailable, scoring fails and an error event is logged.
   - If yes, save prompt as `*_config_vX.Y.Z.yaml` in `01-examples/`
   - If no, run `PromptImprovementAgent` to create improved prompt
6. **Log improved prompt and feedback**
7. **Run `ControllerAgent` for alignment and decision**
8. **Repeat improvement loop up to max iterations or until aligned**
9. **When stable, move prompt to `*_active_vX.Y.Z.yaml` in `02-production/`**

### Logging

All intermediate states are logged in `/logs/` under these categories:

- `prompt_log/`
- `quality_log/`
- `feedback_log/`
- `change_log/`
- `score_log/`

Each log entry is a fully validated JSON event for traceability and monitoring.

## Best Practices

- Use consistent **snake_case** and lowercase for filenames.
- Avoid whitespaces or special characters in filenames.
- Keep YAML templates valid and under version control.
- Archive old logs regularly to maintain performance.
- Keep scoring and configuration files versioned in `config/`.
- Ensure prompt versions inside files and filenames always match.

### Placeholder Feedback

`PromptQualityAgent` can generate detailed feedback for specific positions in a
prompt. Placeholders in curly braces remain supported, but you can now also use
explicit tags (`[[placeholder]]`). Additionally, common YAML fields such as
`id`, `objective` and `constraints` are automatically evaluated even when they
contain no braces.

Example snippet:

```yaml
id: contact_assignment
objective: >
  [[objective]]
constraints:
  - [[constraints]]
```

Detected placeholders are listed in the `detailed_feedback` section of the
quality check result.

## Deployment Targets

Production prompts (`*_active_vX.Y.Z.yaml`) are ready for deployment to:

- AWS App Runner, Docker, or container orchestration platforms
- Static S3 buckets or API gateway endpoints for retrieval
- Integration pipelines with CRM or third-party APIs

---

> This repo and workflow enable scalable, traceable, and iterative prompt engineering to support enterprise-grade AI applications with full version control, logging, and auditability.

---
