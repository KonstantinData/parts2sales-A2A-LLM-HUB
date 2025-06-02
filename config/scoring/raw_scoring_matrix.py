"""
raw_scoring_matrix.py

Purpose : Scoring matrix for initial RAW prompt quality validation.
Version : 1.0.0
Author  : Konstantin’s AI Copilot
Notes   :
- Key integration: Used by PromptQualityAgent for raw layer QC
- Handles clarity, format, structure, basic evaluability, and ambiguity
- Usage: Pass as scoring_matrix_name="raw" to agent
"""

SCORING_MATRIX = {
    "clarity": 1.2,  # Prompt goal clear and unambiguous?
    "format_consistency": 1.1,  # YAML/JSON structure correct?
    "initial_structure": 1.0,  # All required fields present?
    "evalability": 1.1,  # Output evaluable (not open-ended)?
    "ambiguity_avoidance": 1.0,  # No ambiguous requirements?
}
