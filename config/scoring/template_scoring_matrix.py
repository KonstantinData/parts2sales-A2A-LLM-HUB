"""
Template Scoring Matrix

This module defines the evaluation dimensions and weights used to assess the quality of prompt templates
*prior* to their execution. The scoring focuses exclusively on aspects intrinsic to the prompt structure,
clarity, and alignment – not on the quality of generated results.

Usage:
- Imported by agents responsible for evaluating prompt formulations.
- Intended for use in workflows that improve prompt instructions iteratively.
- Should be kept separate from scoring schemes that evaluate LLM-generated outputs (e.g., `example_scoring_matrix.py`).

"""

TEMPLATE_SCORING_MATRIX = {
    "task_clarity": 1.0,  # Is the task clearly described?
    "output_spec": 1.0,  # Is the expected output format specified?
    "structure_check": 0.9,  # Is the prompt structurally consistent (e.g., YAML format)?
    "constraint_clarity": 1.1,  # Are constraints or rules clearly defined?
    "reasoning_scope": 1.2,  # Does the prompt support traceable reasoning?
    "evalability": 1.3,  # Is the output evaluable?
    "ambiguity_avoidance": 1.0,  # Does the prompt avoid ambiguous phrasing?
    "domain_alignment": 0.8,  # Is the prompt aligned with its domain (e.g., B2B context)?
    "composability": 0.7,  # Is the prompt modular and extendable?
    "user_alignment": 1.2,  # Is the prompt aligned with the intended user need?
}
