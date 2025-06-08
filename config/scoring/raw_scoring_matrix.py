"""
Raw Prompt Quality Scoring Matrix

Defines evaluation criteria for assessing the quality of a raw prompt.
Each criterion includes:
- weight: relative impact on the total score
- description: purpose of the criterion
- llm_score_prompt: how to ask the LLM to rate it (0–1)
- llm_feedback_prompt: how to ask the LLM to provide suggestions

Used by the PromptQualityAgent before prompt deployment.

Author: Konstantin Milonas
Version: 2.0
"""

SCORING_MATRIX = {
    "goal_clarity": {
        "weight": 1.2,
        "description": "Does the prompt clearly define the user's goal and the expected behavior of the LLM?",
        "llm_score_prompt": "Rate how clearly the prompt defines the user's goal and expected LLM behavior (0–1):",
        "llm_feedback_prompt": "Suggest how the prompt's goal and expectations could be expressed more clearly.",
    },
    "role_specification": {
        "weight": 1.0,
        "description": "Does the prompt define the LLM's role or perspective with sufficient precision?",
        "llm_score_prompt": "Rate the precision of the role or persona defined for the LLM (0–1):",
        "llm_feedback_prompt": "How could the role or perspective of the LLM be specified more clearly?",
    },
    "structure_completeness": {
        "weight": 1.1,
        "description": "Are all structural components present (e.g., input/output schema, constraints)?",
        "llm_score_prompt": "Rate the completeness of structural components (input/output schema, constraints) (0–1):",
        "llm_feedback_prompt": "Suggest missing or unclear structural elements that should be added.",
    },
    "constraint_enforcement": {
        "weight": 1.1,
        "description": "Are formatting and behavioral constraints clearly stated and enforceable?",
        "llm_score_prompt": "How well does the prompt enforce clear behavioral and formatting constraints (0–1):",
        "llm_feedback_prompt": "Suggest improvements to constraints to avoid ambiguous or invalid outputs.",
    },
    "evalability": {
        "weight": 1.1,
        "description": "Can the generated output be evaluated clearly and objectively?",
        "llm_score_prompt": "How easy is it to evaluate the correctness of the output given the prompt (0–1):",
        "llm_feedback_prompt": "Suggest how to make the output more evaluable or testable.",
    },
    "ambiguity_avoidance": {
        "weight": 1.0,
        "description": "Is the prompt free of contradictions, ambiguities, or vagueness?",
        "llm_score_prompt": "Rate how free the prompt is from ambiguity or contradictions (0–1):",
        "llm_feedback_prompt": "Identify any ambiguous or contradictory phrasing and suggest a fix.",
    },
    "error_handling_readiness": {
        "weight": 0.8,
        "description": "Does the prompt define what should happen in case of incomplete or missing inputs?",
        "llm_score_prompt": "Rate the prompt's preparedness for missing or invalid inputs (0–1):",
        "llm_feedback_prompt": "Suggest how to improve the prompt's error handling readiness.",
    },
}


def compute_weighted_score(
    prompt_scores: dict[str, float], matrix: dict = SCORING_MATRIX
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
