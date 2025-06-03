"""
base_agent.py

Purpose : Abstract base class for all agent implementations.
Logging : Designed for workflow-centric JSONL logging with JsonlEventLogger (to be used by subclasses).

Author  : Konstantin Milonas with support from AI Copilot

# Notes:
# - Establishes interface and patterns for all concrete agent subclasses.
# - Promotes standardized logging, error handling, and DI for all child agents.
# - Encourages passing workflow_id for full traceability.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Concrete agents must implement the run() method and are encouraged to use
    workflow-centric JSONL logging.
    """

    def __init__(self, log_dir: Path = Path("logs/workflows")):
        """
        log_dir: Directory for workflow logs.
        """
        self.log_dir = log_dir

    @abstractmethod
    def run(
        self,
        input_path: Path,
        base_name: str,
        iteration: int,
        workflow_id: Optional[str] = None,
    ):
        """
        Entry point for agent execution. Must be implemented by subclasses.

        Args:
            input_path: Path to the input file or data.
            base_name: Name or version of the prompt/workflow.
            iteration: Current iteration count or step.
            workflow_id: Unique workflow/session ID for JSONL logging.

        Returns:
            Should return the relevant AgentEvent or result object.
        """
        pass
