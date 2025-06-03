from enum import Enum


class ImprovementStrategy(Enum):
    LLM = "LLM"  # Use Large Language Model for improvement
    RULE_BASED = "RULE_BASED"  # Use hard-coded or config rules
    CUSTOM = "CUSTOM"  # Any project-specific/custom logic
    HUMAN_IN_LOOP = "HUMAN"  # (Optional) For human/manual review
    HYBRID = "HYBRID"  # (Optional) For hybrid approaches
    # Add more as needed


# Optionally, add docstrings or comments for each strategy
