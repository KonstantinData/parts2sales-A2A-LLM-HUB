# config/scoring/template_scoring_matrix.py

TEMPLATE_SCORING_MATRIX = {
    "output_structure": {
        "weight": 0.4,
        "description": "Structure and clarity of the returned JSON (e.g., correct keys, types, nesting)",
        "feedback": "The output JSON is missing required fields or is misstructured.",
    },
    "output_relevance": {
        "weight": 0.3,
        "description": "Relevance of the generated output to the prompt's stated objective",
        "feedback": "The output does not sufficiently address the purpose defined in the prompt.",
    },
    "output_language_quality": {
        "weight": 0.2,
        "description": "Spelling, grammar, and fluency of the generated output",
        "feedback": "The language in the output is unclear or contains errors.",
    },
    "output_completeness": {
        "weight": 0.1,
        "description": "Coverage of required details in the output",
        "feedback": "The output is missing important elements requested in the prompt.",
    },
}

# Note: scoring logic might be deprecated if moving to agent-based self-assessment and improvement system


def compute_weighted_score(
    prompt_scores: dict[str, float], matrix: dict = TEMPLATE_SCORING_MATRIX
) -> float:
    """
    Compute the weighted average score based on LLM-evaluated criteria.

    Parameters:
        prompt_scores (dict): key = criterion name, value = LLM score (0.0–1.0)
        matrix (dict): scoring matrix to apply

    Returns:
        float: weighted final score between 0.0 and 1.0
    """
    weighted_sum = 0.0
    total_weight = 0.0

    for criterion, score in prompt_scores.items():
        if criterion in matrix:
            weight = matrix[criterion]["weight"]
            weighted_sum += score * weight
            total_weight += weight

    if total_weight == 0.0:
        return 0.0
    return round(weighted_sum / total_weight, 4)
