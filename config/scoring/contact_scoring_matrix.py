"""
Contact Match Scoring Matrix

Evaluation matrix for prompt quality in contact-to-product or company matching scenarios.

Usage:
- Used by PromptQualityAgent for evaluating prompts that map contacts to relevant offerings.
- Supports high-precision, evaluable, and context-aware matching.
"""

SCORING_MATRIX = {
    "match_relevance": {
        "weight": 1.3,
        "description": "Are the matched contacts directly relevant to the product or context?",
        "feedback": "Contact match appears irrelevant or too generic. Adjust prompt to focus on roles or contexts aligned with the offering.",
    },
    "confidence": {
        "weight": 1.2,
        "description": "Does the model provide clear confidence or reasoning for the match?",
        "feedback": "Confidence signals are weak or missing. Encourage explanation or indicators in the output.",
    },
    "clarity": {
        "weight": 1.0,
        "description": "Is the prompt clearly structured for the task?",
        "feedback": "Prompt is not clearly phrased. Refactor for better readability and clarity.",
    },
    "evalability": {
        "weight": 1.1,
        "description": "Is the contact match output easy to evaluate?",
        "feedback": "Evaluation is difficult due to vague output. Guide the model to produce verifiable responses.",
    },
    "ambiguity_avoidance": {
        "weight": 1.0,
        "description": "Is the prompt formulated to avoid ambiguity in matching criteria?",
        "feedback": "Ambiguous matching detected. Use more specific criteria or examples in the prompt.",
    },
}
