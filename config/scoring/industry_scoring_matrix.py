"""
Industry Classification Scoring Matrix

Criteria for prompts classifying product industry sectors.

Usage:
- Used by PromptQualityAgent when scoring industry classification prompts.
"""

INDUSTRY_SCORING_MATRIX = {
    "classification_accuracy": 1.3,  # Accuracy of industry classification
    "clarity": 1.1,  # Clarity of instructions
    "evalability": 1.2,  # Ease of evaluating classification output
    "domain_alignment": 1.0,  # Alignment with domain taxonomy
}
