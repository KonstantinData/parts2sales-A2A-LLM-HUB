"""
company_scoring_matrix.py

Purpose : Scoring matrix for evaluating prompts matching companies to products/services.
Version : 1.0.0
Author  : Konstantin & AI Copilot
Notes   :
- Focus on match relevance, confidence, business domain alignment, and evaluability
- Used by CompanyMatchAgent for company-level matchmaking QC
"""

SCORING_MATRIX = {
    "match_relevance": 1.3,  # Relevance of the match for the target company
    "confidence": 1.2,  # Confidence in the match according to output
    "business_domain_alignment": 1.1,  # Alignment with company industry/domain
    "clarity": 1.0,  # Prompt clarity
    "evalability": 1.1,  # Is the output easy to evaluate?
    "ambiguity_avoidance": 1.0,  # Does the prompt avoid ambiguous instructions?
}
