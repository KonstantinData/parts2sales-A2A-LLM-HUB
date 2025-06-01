# 🧪 Layer: `prompt_quality/`

## 🎯 Purpose
This module provides CLI tools and validation logic to assess the **linguistic quality**, **structural clarity**, and **metadata integrity** of prompts before moving them into production.

---

## 🔧 Responsibilities

- Validate prompt grammar, tone, idiomatic phrasing, structure, and task clarity.
- Execute multi-language quality checks for **English** and **German** using custom rule sets.
- Combine templates with example inputs and simulate full prompt flow.
- Log validation outputs for reproducibility and iterative prompt design.
- Verify YAML metadata structure in production-bound prompt registries.

---

## 📁 Structure

```
prompt_quality/
├── cli/
│   ├── validate_prompt_quality_cli.py
│   └── render_and_validate_template.py
├── languages/
│   ├── lang_en.py
│   └── lang_de.py
├── validators/
│   ├── validate_prompt_quality_en.py
│   └── validate_prompt_quality_de.py
├── logs//
│   └── prompt_quality_*.log
```

---

## 📊 Validation Criteria

- ✅ Linguistic: Idioms, tone of voice, action verbs, structure
- ✅ Structural: Placeholder alignment, length limits, clarity
- ✅ Metadata: Key presence, prompt registry compliance

---

## 📂 Logs
- Output is stored in `prompt_quality/logs/`
- Timestamped per run
- Shows failed criteria and suggested fixes

---

## 🧩 Use in CI
- Run as pre-merge step to ensure prompt integrity
- Output logs are useful as reviewer guidance in PRs
- Integrates well with workflows that generate or validate prompts dynamically

---

## 🧠 Best Practices

- Regularly update `lang_*.py` rule sets with feedback from LLM output evaluations
- Use CLI locally for debugging before submitting prompts
- Keep logs for reproducibility & compliance

---

## 🧭 Strategic Impact

By enforcing quality at this stage, Liquisto ensures prompt clarity, mitigates downstream risk, and aligns tone across languages and user-facing LLM components.
