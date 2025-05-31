# 🧪 Prompt Examples

This directory contains structured JSON files with **example input/output pairs** for each task.

## Purpose
- Serve as test and validation data for prompts
- Power CI/CD scoring and quality gates
- Provide a reproducible audit trail

## Structure
Each task has its own subdirectory:
```
prompts/01-examples/<task_id>/
```

Each file includes:
```json
{
  "input": { ... },
  "expected": { ... }
}
```

## Rules
- File format: `.json`
- Keys must match `input_format` and `output_format` from `02-production`
- Avoid fictional or placeholder brands — use anonymized real-world examples if possible

## Usage
These examples are invoked by:
- `scripts/eval_runner.py`
- GitHub Actions → `ci.yml`