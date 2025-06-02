"""
Feature Extraction Scoring Matrix

Evaluation criteria for prompts used in feature extraction from product data.

Usage:
- Used by PromptQualityAgent when scoring feature extraction prompts.
"""

SCORING_MATRIX = {
    "feature_coverage": 1.2,  # Does the prompt extract all relevant features?
    "precision": 1.1,  # Is feature extraction precise and unambiguous?
    "format_consistency": 1.0,  # Is the output format consistent for features?
    "clarity": 1.0,  # Is the prompt clear and concise?
    "evalability": 1.3,  # Is the output evaluable for quality?
    "domain_relevance": 1.0,  # Is the prompt aligned with the product domain?
}
