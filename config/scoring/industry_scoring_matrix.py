"""
Industry Classification Scoring Matrix

Evaluation matrix for assessing prompt quality in classifying products into industry sectors.

Usage:
- Used by PromptQualityAgent when scoring industry classification prompts.
- Promotes clarity, accuracy, and taxonomy-aligned classification.
"""

SCORING_MATRIX = {
    "classification_accuracy": {
        "weight": 1.3,
        "description": "Does the output assign the correct industry classification?",
        "feedback": "Industry classification is inaccurate. Refine the prompt to better align with established taxonomies or provide clearer classification hints.",
    },
    "clarity": {
        "weight": 1.1,
        "description": "Are the instructions for classification clearly stated?",
        "feedback": "Prompt is unclear. Improve clarity to ensure the classification task is unambiguous.",
    },
    "evalability": {
        "weight": 1.2,
        "description": "Is the classification output structured for easy evaluation?",
        "feedback": "Output lacks evaluable structure. Prompt should instruct for standardized or taxonomy-aligned responses.",
    },
    "domain_alignment": {
        "weight": 1.0,
        "description": "Is the classification aligned with the product’s actual domain?",
        "feedback": "Mismatch in domain alignment. Ensure prompt accounts for relevant product sector or usage context.",
    },
}
