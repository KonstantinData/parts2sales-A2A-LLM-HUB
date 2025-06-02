"""
base_agent.py

Purpose : Abstract base class for all agent types in the system; enforces unified agent interface.
Version : 1.1.0
Author  : Konstantin & AI Copilot
Notes   :
- Each agent must subclass BaseAgent and implement `run()`.
- Enforces plug-and-play, type-safe workflow integration.
- Use for static typing, documentation, and future extension (e.g., logging, hooks).
"""

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Abstract base class for all LLM agents."""

    def __init__(self, name: str):
        self.name = name  # Each agent can be uniquely identified

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        Executes the main logic of the agent.
        Returns:
            Any: Can be a score, improved artifact, or evaluation event.
        """
        pass
