# usecase_quality_score.py

# ------------------------------------------

# Purpose:
# Provide scoring logic based on prompt validation results

# Goals:
# - Convert validation outcomes to a numeric score (0–100)
# - Penalize each failed check equally

# Use Cases:
# - Score feedback in validation logs
# - CI threshold checks


def score_validated_row(row: dict) -> int:
    violations = row.get("violations", [])
    total_checks = 7  # total number of validation dimensions
    passed = total_checks - len(violations)
    score = int((passed / total_checks) * 100)
    return score
