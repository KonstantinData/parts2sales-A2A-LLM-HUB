"""
feature_scoring_matrix.py

Feature Extraction Scoring Matrix & Output Validator

Defines evaluation criteria for prompts used in feature extraction from product data.
Also provides:
- A utility function to validate actual prompt output against expectations.
- A weighted scoring function to compute final LLM evaluation scores.

Author: Konstantin Milonas
Version: 1.2
"""

SCORING_MATRIX = {
    "feature_coverage": {
        "weight": 1.2,
        "description": "Does the output include a complete and representative set of relevant features?",
        "feedback": "The output might miss some relevant product features. Consider ensuring all physical, electrical, mechanical, and regulatory properties are covered.",
    },
    "precision": {
        "weight": 1.1,
        "description": "Are the extracted features unambiguous and strictly objective?",
        "feedback": "Ensure the prompt avoids vague or inferred feature descriptions. Focus on measurable specifications only.",
    },
    "format_consistency": {
        "weight": 1.0,
        "description": "Is the output format strictly aligned with the defined schema and machine-readable?",
        "feedback": "The output format appears inconsistent or not schema-conform. Define a rigid output structure using clear type declarations.",
    },
    "clarity": {
        "weight": 1.0,
        "description": "Is the structure of the output understandable to both humans and downstream systems?",
        "feedback": "Clarify the meaning and expected format of each field to improve readability and integration.",
    },
    "evalability": {
        "weight": 1.3,
        "description": "Can the output be easily evaluated with automated tools or tests?",
        "feedback": "Add schema definitions and consistency rules that allow automated validation of the output.",
    },
    "domain_relevance": {
        "weight": 1.0,
        "description": "Is the output aligned with the semantics of industrial product data?",
        "feedback": "Ensure the extracted features are relevant to the domain (e.g., technical specs, certifications, materials).",
    },
}


def validate_output_conformity(output: dict) -> tuple[bool, list[str]]:
    """
    Validates the structure and content of a prompt output.

    Returns:
        - True if output is valid, otherwise False
        - A list of validation error messages
    """
    errors = []

    if "features" not in output:
        return False, ["Missing top-level key: 'features'"]
    if not isinstance(output["features"], list):
        return False, ["'features' must be a list"]

    allowed_sources = {"title", "part_number", "manufacturer"}

    for i, feature in enumerate(output["features"]):
        if not isinstance(feature, dict):
            errors.append(f"Feature #{i} is not a dictionary")
            continue

        for key in ("name", "value", "source"):
            if key not in feature:
                errors.append(f"Missing key '{key}' in feature #{i}")

        if "name" in feature and not isinstance(feature["name"], str):
            errors.append(f"'name' in feature #{i} must be a string")
        if "value" in feature and not isinstance(feature["value"], str):
            errors.append(f"'value' in feature #{i} must be a string")
        if (
            "unit" in feature
            and feature["unit"] is not None
            and not isinstance(feature["unit"], str)
        ):
            errors.append(f"'unit' in feature #{i} must be a string or omitted")
        if "source" in feature and feature["source"] not in allowed_sources:
            errors.append(f"'source' in feature #{i} must be one of {allowed_sources}")

    return len(errors) == 0, errors


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
