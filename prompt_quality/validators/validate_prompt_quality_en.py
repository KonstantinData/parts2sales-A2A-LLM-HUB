"""
Purpose:
Perform detailed quality checks on English LLM prompts.

Goals:
- Use grammar validation (language_tool_python)
- Apply idiomatic, lexical, structural and tone checks

Use Cases:
- Used by CLI tools and test scripts to validate prompt quality
"""

import language_tool_python
from prompt_quality.languages import lang_en


def validate_prompt_en(prompt_text: str) -> dict:
    tool = language_tool_python.LanguageTool("en-US")

    # Grammar check (YAML-Formate teilweise aussparen)
    grammar_matches = [
        m for m in tool.check(prompt_text) if not m.ruleId.startswith("WHITESPACE")
    ]
    grammar_passed = len(grammar_matches) == 0

    # Idioms
    idiom_passed, idiom_matches = lang_en.has_idiom(prompt_text)

    # Task clarity
    task_passed, task_hits = lang_en.is_actionable(prompt_text)

    # Structure
    structure_passed, structure_hits = lang_en.has_structure(prompt_text)

    # Lexical rules (bool & matches)
    lexical_ok, lexical_violations = lang_en.violates_lexical_rules(prompt_text)
    lexical_passed = lexical_ok

    # Tone check (bool & matches)
    tone_ok, tone_issues = lang_en.has_tone_issue(prompt_text)
    tone_passed = tone_ok

    # Combined clarity/integrity
    translation_integrity = grammar_passed and task_passed

    tool.close()

    return {
        "grammar_check": {
            "passed": grammar_passed,
            "examples": (
                [m.message for m in grammar_matches] if not grammar_passed else []
            ),
        },
        "idiomatic_check": {
            "passed": idiom_passed,
            "examples": idiom_matches if not idiom_passed else [],
        },
        "task_clarity": {
            "passed": task_passed,
            "examples": task_hits if not task_passed else [],
        },
        "structure_check": {
            "passed": structure_passed,
            "examples": structure_hits if not structure_passed else [],
        },
        "lexical_fit": {
            "passed": lexical_passed,
            "examples": lexical_violations if not lexical_passed else [],
        },
        "tone_check": {
            "passed": tone_passed,
            "examples": tone_issues if not tone_passed else [],
        },
        "translation_integrity": {
            "passed": translation_integrity,
            "examples": (
                []
                if translation_integrity
                else ["Check grammar and instruction intent."]
            ),
        },
    }
