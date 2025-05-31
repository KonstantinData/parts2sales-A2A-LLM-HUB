# 🚀 Production Prompts

This folder contains **versioned, validated YAML prompt definitions** ready for live inference or CI evaluation.

## Purpose
- Provide deterministic, tested prompts
- Power runtime classification, extraction, or scoring
- Serve as canonical version source for downstream tools

## Structure
Each file follows:
```
<task_id>_v<version>.yaml
```

## Requirements
- Must include `id`, `version`, `created_by`, `input_format`, `output_format`
- Fully test-covered in `01-examples/`
- Used in CI scoring and ECS deployment

## Constraints
- Cannot include test code or placeholders
- Must return JSON-compliant, model-ready format
- Version bumps must follow semver and update `03-metadata/`