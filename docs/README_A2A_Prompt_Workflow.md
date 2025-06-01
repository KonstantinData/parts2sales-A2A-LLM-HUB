# A2A Prompt Engineering Workflow

## Project Structure

```
.
├── 00-structure/              # Raw structured prompt blueprints
├── 01-research/               # Evaluation-ready drafts/templates from raw files
├── 02-laboratory/             # Post-evaluation optimization experiments
├── 03-production/             # Validated and system-integrated prompts
├── config/                    # Configuration files for scoring and templates
├── logs/                      # All generated logs (prompt, quality, feedback, etc.)
├── prompts/                   # Entry folder for structured YAML prompts
└── cli/                       # CLI scripts to automate workflows
```

## Naming Convention & Semantic Versioning

All prompt files follow this semantic versioning and suffix convention:

- `*_raw_v1.yaml` – untested structural base
- `*_templ_v1.yaml` – formatted and draft-ready
- `*_config_v1.yaml` – tested and refined via lab
- `*_active_v1.yaml` – in-use production prompt

**Examples:**

| Purpose                 | Filename Example                  |
| ----------------------- | --------------------------------- |
| Company assignment      | `company_assign_raw_v1.yaml`    |
| Contact assignment      | `contact_assign_templ_v2.yaml`  |
| Feature setup           | `feature_setup_active_v3.yaml`  |
| Industry classification | `industry_class_config_v2.yaml` |
| Use case detection      | `usecase_detect_active_v1.yaml` |

Semantic Versioning used in `version:` field and filenames:

| SemVer | Meaning                           |
| ------ | --------------------------------- |
| 0.x.y  | Experimental or beta phase        |
| 1.0.0  | First stable production release   |
| 1.x.y  | Backwards-compatible feature/fix  |
| 2.0.0  | Major redesign / breaking changes |

## Workflow Description

The workflow proceeds as follows:

1. **Start Event**
2. **Read Prompt V1 File**
3. **Write Prompt Log (v1)**
4. **Run PromptQualityAgent**
5. **Write Quality Log**
6. **Write Weighted Score Log**
7. **Evaluate Score ≥ Threshold?**
   - If yes → Save Final Prompt to `01-research`
   - If no  → Run PromptImprovementAgent
8. **Write Improved Prompt**
9. **Log Prompt (v2)**
10. **Write Feedback Log**
11. **Write Change Log**
12. **Run ControllerAgent**
13. **Check Alignment**
    - If aligned → loop back to quality check
    - If not aligned → retry up to limit
14. **Abort if retries exceed limit**

All intermediate logs are saved under `/logs`. Each versioned improvement produces:

- `prompt_log/`
- `quality_log/`
- `feedback_log/`
- `change_log/`
- `weighted_score/`

## Best Practices

- Use **snake_case** and **lowercase** in filenames.
- Avoid whitespace and special characters.
- Archive old logs if not used.
- YAML templates must remain valid and version-controlled.
- Keep `config/` versioned for scoring consistency.

## Deployment Targets

Production prompts from `03-production/` may be deployed via:

- **AWS App Runner**
- **Docker Container Services**
- **S3 Buckets or API Gateways**

---

> This repo is structured to support scalable, iterative LLM prompt development with high reproducibility and log traceability.
