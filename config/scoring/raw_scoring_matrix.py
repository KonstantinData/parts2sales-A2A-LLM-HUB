# config/scoring/raw_scoring_matrix.py

"""
Raw Prompt Quality Scoring Matrix

LLM-native evaluation matrix with:
- weight: impact on total score
- description: semantic meaning of the criterion
- llm_score: numerical rating prompt (0–1 scale)
- llm_feedback: free-form suggestion request

# config/scoring/raw_scoring_matrix.py

This matrix is used by the PromptQualityAgent for LLM-based evaluation
of raw prompt quality before functional assessment.
"""

SCORING_MATRIX = {
    "clarity": {
        "weight": 1.2,
        "description": "Does the prompt clearly express the user's goal and expected output?",
        "llm_score": "On a scale between 0 and 1, how would you rate the clarity of the prompt's goal and output?",
    },
    "format_consistency": {
        "weight": 1.1,
        "description": "Is the prompt formatted consistently and validly (e.g., YAML, JSON)?",
        "llm_score": "On a scale between 0 and 1, how consistent and valid is the format of the prompt?",
    },
    "initial_structure": {
        "weight": 1.0,
        "description": "Does the prompt include all required structural elements (e.g., metadata, instruction, output schema)?",
        "llm_score": "On a scale between 0 and 1, how complete and well-structured is the initial prompt layout?",
    },
    "evalability": {
        "weight": 1.1,
        "description": "Can the expected output be clearly evaluated based on the given instruction?",
        "llm_score": "On a scale between 0 and 1, how well does the prompt support objective evaluation of the output?",
    },
    "ambiguity_avoidance": {
        "weight": 1.0,
        "description": "Are there any vague, conflicting or ambiguous instructions present?",
        "llm_score": "On a scale between 0 and 1, how free is the prompt from ambiguity or contradictions?",
    },
}


def compute_weighted_score(prompt_scores: dict[str, float]) -> float:
    """
    Compute the weighted average score based on LLM-evaluated criteria.

    Parameters:
        prompt_scores (dict): key = criterion name, value = LLM score (0.0–1.0)

    Returns:
        float: weighted final score between 0.0 and 1.0
    """
    weighted_sum = 0.0
    total_weight = 0.0

    for criterion, score in prompt_scores.items():
        if criterion in SCORING_MATRIX:
            weight = SCORING_MATRIX[criterion]["weight"]
            weighted_sum += score * weight
            total_weight += weight

    if total_weight == 0:
        return 0.0
    return weighted_sum / total_weight
