"""
Company Match Scoring Matrix

Evaluation matrix for assessing prompt quality when matching companies to relevant products or services.

Usage:
- Used by CompanyMatchAgent during quality control of company match prompts.
- Ensures high relevance, domain fit, and evaluability in matching logic.
"""

SCORING_MATRIX = {
    "match_relevance": {
        "weight": 1.3,
        "description": "Is the proposed match strongly relevant for the target company’s needs or profile?",
        "feedback": "The match appears weak or misaligned. Refine the prompt to focus on product-service fit for the specific company context.",
    },
    "confidence": {
        "weight": 1.2,
        "description": "Does the output convey strong internal confidence in the match (e.g., justified rationale)?",
        "feedback": "The prompt produces low-confidence outputs. Encourage rationale generation or confidence estimates in the answer.",
    },
    "business_domain_alignment": {
        "weight": 1.1,
        "description": "Does the match align with the company's industry or operational domain?",
        "feedback": "Mismatch detected between suggested match and business domain. Ensure the prompt considers industry-specific factors.",
    },
    "clarity": {
        "weight": 1.0,
        "description": "Is the prompt clearly phrased and easy to interpret?",
        "feedback": "The prompt is unclear. Improve structure and wording for better interpretability.",
    },
    "evalability": {
        "weight": 1.1,
        "description": "Is the output from the prompt structured and evaluable for correctness?",
        "feedback": "Output is hard to evaluate. Restructure prompt to produce verifiable and assessable answers.",
    },
    "ambiguity_avoidance": {
        "weight": 1.0,
        "description": "Does the prompt minimize the risk of ambiguous or conflicting instructions?",
        "feedback": "Ambiguity found. Reformulate to avoid misinterpretation.",
    },
}
