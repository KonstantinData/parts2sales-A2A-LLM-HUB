"""
feature_scoring_matrix.py

Feature Extraction Scoring Matrix

Evaluation criteria for prompts used in feature extraction from product data.

Usage:
- Used by PromptQualityAgent when scoring feature extraction prompts.
- Each criterion includes a weight and a feedback text for dynamic improvement hints.
"""

SCORING_MATRIX = {
    "feature_coverage": {
        "weight": 1.2,  # Does the prompt extract all relevant features?
        "description": "Does the prompt extract all relevant features from the input data?",
        "feedback": "The prompt may be missing some relevant features. Consider expanding the extraction scope to cover all necessary product attributes.",
    },
    "precision": {
        "weight": 1.1,  # Is feature extraction precise and unambiguous?
        "description": "Is the feature extraction precise, avoiding ambiguity or generalization?",
        "feedback": "The prompt lacks precision. Make sure the extraction criteria are clear and unambiguous to avoid imprecise or incorrect feature identification.",
    },
    "format_consistency": {
        "weight": 1.0,  # Is the output format consistent for features?
        "description": "Is the output format consistent and standardized across all features?",
        "feedback": "The output format is inconsistent. Define a clear and consistent format for the feature extraction results to facilitate evaluation and further processing.",
    },
    "clarity": {
        "weight": 1.0,  # Is the prompt clear and concise?
        "description": "Is the prompt formulated clearly and concisely for easy understanding?",
        "feedback": "The prompt is unclear or verbose. Simplify and clarify the instructions to ensure the LLM understands the extraction task effectively.",
    },
    "evalability": {
        "weight": 1.3,  # Is the output evaluable for quality?
        "description": "Can the output be easily evaluated for correctness and completeness?",
        "feedback": "The prompt output is difficult to evaluate. Structure the prompt to produce output that can be quantitatively or qualitatively assessed reliably.",
    },
    "domain_relevance": {
        "weight": 1.0,  # Is the prompt aligned with the product domain?
        "description": "Is the prompt relevant and tailored to the specific product domain?",
        "feedback": "The prompt lacks domain-specific focus. Ensure it targets the relevant product area to improve the relevance and usefulness of extracted features.",
    },
}
