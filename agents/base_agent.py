"""
base_agent.py

Purpose : Abstract base class for all LLM agents (standardized interface).
Version : 1.0.0
Author  : Konstantin & AI Copilot
Notes   :
- All agents must implement `run()`
- Promotes pluggability and unified integration in pipelines
- Add agent name for unique identification/logging
- Subclass in: PromptQualityAgent, PromptImprovementAgent, ControllerAgent, etc.
"""

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Abstract base class for all LLM agents."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        Execute the main logic of the agent.
        Returns:
            Any (score, artifact, result object, etc.)
        """
        pass
