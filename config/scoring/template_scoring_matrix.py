"""
Template Design Scoring Matrix

Evaluation matrix for validating prompt templates before runtime. Focuses on clarity, structure, composability, and user alignment.

Usage:
- Used by PromptQualityAgent to evaluate prompt templates.
- Focused on pre-execution prompt logic and structure.
"""

SCORING_MATRIX = {
    "task_clarity": {
        "weight": 1.0,
        "description": "Is the task or instruction clearly stated and unambiguous?",
        "feedback": "Prompt task unclear. Define goals explicitly and simply.",
    },
    "output_spec": {
        "weight": 1.0,
        "description": "Is the expected output format defined and consistent?",
        "feedback": "Expected output format missing or inconsistent. Define expected structure (e.g., YAML, JSON, list).",
    },
    "structure_check": {
        "weight": 0.9,
        "description": "Is the prompt structurally valid (e.g., indentations, headers)?",
        "feedback": "Prompt structure flawed. Correct layout and syntax to avoid confusion.",
    },
    "constraint_clarity": {
        "weight": 1.1,
        "description": "Are task constraints or rules clearly stated and enforceable?",
        "feedback": "Constraints unclear or missing. Explicitly list any rules or limits for the task.",
    },
    "reasoning_scope": {
        "weight": 1.2,
        "description": "Does the prompt allow for traceable or explainable reasoning?",
        "feedback": "Prompt does not support reasoning transparency. Encourage reasoning or chain-of-thought in the output.",
    },
    "evalability": {
        "weight": 1.3,
        "description": "Can the output be easily evaluated for correctness and quality?",
        "feedback": "Output is hard to evaluate. Guide format and content for better assessability.",
    },
    "ambiguity_avoidance": {
        "weight": 1.0,
        "description": "Does the prompt avoid vague or ambiguous phrasing?",
        "feedback": "Prompt is ambiguous. Use clearer phrasing or examples to clarify.",
    },
    "domain_alignment": {
        "weight": 0.8,
        "description": "Is the prompt aligned with its domain or context?",
        "feedback": "Prompt appears misaligned with its use case. Adapt vocabulary or examples to match the domain.",
    },
    "composability": {
        "weight": 0.7,
        "description": "Is the prompt modular and reusable across contexts?",
        "feedback": "Prompt is too rigid. Design it to support variation or modular integration.",
    },
    "user_alignment": {
        "weight": 1.2,
        "description": "Is the prompt aligned with user needs or usage context?",
        "feedback": "Prompt misaligned with user needs. Refactor to reflect typical user expectations or roles.",
    },
}
