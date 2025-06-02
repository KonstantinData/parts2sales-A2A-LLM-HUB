"""
Contact Matching Scoring Matrix

Scoring criteria for prompts that match companies/contacts to products.

Usage:
- Used by PromptQualityAgent when scoring contact/company matching prompts.
"""

CONTACT_SCORING_MATRIX = {
    "match_relevance": 1.3,  # Relevance of matched contacts
    "confidence": 1.2,  # Confidence scoring of matches
    "clarity": 1.0,  # Prompt clarity
    "evalability": 1.1,  # Ease of evaluation
    "ambiguity_avoidance": 1.0,  # Avoids ambiguous matching instructions
}
