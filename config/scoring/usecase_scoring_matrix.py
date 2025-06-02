"""
Use Case Detection Scoring Matrix

Defines criteria for prompts that detect product use cases.

Usage:
- Used by PromptQualityAgent when scoring use case detection prompts.
"""

SCORING_MATRIX = {
    "usecase_relevance": 1.3,  # Are relevant use cases identified?
    "completeness": 1.1,  # Is the detection comprehensive?
    "clarity": 1.0,  # Is the prompt clear and well-structured?
    "evalability": 1.2,  # Is the output easy to evaluate?
    "ambiguity_avoidance": 1.0,  # Avoids ambiguous descriptions?
}
