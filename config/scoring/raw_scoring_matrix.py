"""
Raw Prompt Quality Scoring Matrix

Initial scoring matrix for basic prompt validation before deeper functional assessment.

Usage:
- Used by PromptQualityAgent for low-level prompt quality control.
- Focus on structure, clarity, and evaluation-readiness.
"""

SCORING_MATRIX = {
    "clarity": {
        "weight": 1.2,
        "description": "Is the prompt’s intention and target clearly formulated?",
        "feedback": "The goal of the prompt is unclear. Refine language to remove vagueness.",
    },
    "format_consistency": {
        "weight": 1.1,
        "description": "Is the structure of the prompt (YAML/JSON etc.) consistent and valid?",
        "feedback": "Formatting is inconsistent. Use a clear, standardized schema across the prompt.",
    },
    "initial_structure": {
        "weight": 1.0,
        "description": "Are all required fields and sections present in the prompt?",
        "feedback": "Missing fields or disordered sections. Add or reorder fields to meet the expected template.",
    },
    "evalability": {
        "weight": 1.1,
        "description": "Is the output designed for evaluability (clear, complete, checkable)?",
        "feedback": "Output cannot be reliably evaluated. Provide structures or guidance for better assessment.",
    },
    "ambiguity_avoidance": {
        "weight": 1.0,
        "description": "Does the prompt avoid ambiguous or conflicting statements?",
        "feedback": "Ambiguities present. Simplify and disambiguate task instructions.",
    },
}
