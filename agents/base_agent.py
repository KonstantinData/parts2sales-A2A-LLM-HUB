"""
base_agent.py

Purpose : Provides a base class/interface for all Agents in the LLM orchestration system.
Version : 1.3.0
Author  : Konstantin’s AI Copilot
Notes   :
- Serves as a template for specialized agents (does not use OpenAIClient directly)
- Handles standard attributes and interfaces (e.g., event generation)
- Does not include OpenAI integration (that belongs in child classes)
Usage examples:
    class MyAgent(BaseAgent):
        ...
"""

from typing import Any


class BaseAgent:
    def __init__(self, *args, **kwargs):
        # Standard initialization for all agents
        pass

    def run(self, *args, **kwargs) -> Any:
        raise NotImplementedError("Subclasses must implement 'run' method.")
