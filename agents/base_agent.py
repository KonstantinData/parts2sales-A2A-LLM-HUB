#!/usr/bin/env python3
"""
File: base_agent.py
Type: Python Module (Abstract Base Class)

Purpose:
--------
This module defines a base class for all agent types in the system.
Each agent must implement a `run()` method that takes a structured input
(e.g., prompt path, config object, metadata) and returns an evaluation result or improved artifact.

Usage:
------
This file should be imported and subclassed by all specific agents like:
- PromptQualityAgent
- PromptImprovementAgent

Notes:
------
- Acts as an interface to standardize how agents behave.
- Enables pluggability and unified integration in workflows.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseAgent(ABC):
    """Abstract base class for all LLM agents."""

    def __init__(self, name: str):
        self.name = name  # Note: Each agent can be uniquely identified

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        Executes the main logic of the agent.

        Returns:
            Any: Can be a score, modified file, or result object
        """
        pass
