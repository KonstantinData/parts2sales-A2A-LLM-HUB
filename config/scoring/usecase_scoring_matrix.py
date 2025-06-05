"""
Use Case Detection Scoring Matrix

Evaluation criteria for prompts that detect product use cases from textual or structured input.

Usage:
- Used by PromptQualityAgent when scoring use case detection prompts.
- Helps improve prompt design for comprehensive and relevant use case extraction.
"""

SCORING_MATRIX = {
    "usecase_relevance": {
        "weight": 1.3,
        "description": "Are the identified use cases directly relevant to the product or context?",
        "feedback": "The prompt misses relevant use cases or includes irrelevant ones. Ensure the prompt is tightly scoped to surface truly relevant use cases.",
    },
    "completeness": {
        "weight": 1.1,
        "description": "Does the prompt enable comprehensive extraction of applicable use cases?",
        "feedback": "The output lacks completeness. Reframe the prompt to guide the model toward a broader or more exhaustive set of use cases.",
    },
    "clarity": {
        "weight": 1.0,
        "description": "Is the prompt clearly formulated and free from ambiguity?",
        "feedback": "The prompt may be unclear or confusing. Simplify and clarify the phrasing to enhance understanding.",
    },
    "evalability": {
        "weight": 1.2,
        "description": "Can the use case output be easily evaluated for relevance and correctness?",
        "feedback": "The output is hard to assess. Improve the prompt so that responses are structured and evaluable.",
    },
    "ambiguity_avoidance": {
        "weight": 1.0,
        "description": "Does the prompt avoid vague or ambiguous phrasing that might confuse the model?",
        "feedback": "Ambiguity detected. Use precise language to avoid vague interpretations.",
    },
}
