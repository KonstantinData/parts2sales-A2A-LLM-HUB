#!/usr/bin/env python3
"""
File: controller_agent.py
Type: Python Module (Agent Class)

Purpose:
--------
This agent coordinates the communication between prompt quality and improvement agents.
It ensures that feedback logs reflect quality evaluations and approves or rejects improvements
before allowing prompt re-generation.

If alignment fails, it can signal a retry to the improvement agent, limited to 3 attempts.
"""

import json
from pathlib import Path
from typing import Optional


class ControllerAgent:
    def __init__(
        self, base_name: str, version: int, log_dir: Path, max_retries: int = 3
    ):
        self.base_name = base_name
        self.version = version
        self.log_dir = log_dir
        self.retry_count = 0
        self.max_retries = max_retries

    def _get_log_file(self, category: str, suffix: str) -> Optional[Path]:
        """
        Returns the path to a log file if it exists.
        """
        file_path = self.log_dir / category / f"{self.base_name}_{suffix}.json"
        return file_path if file_path.exists() else None

    def load_json(self, category: str, suffix: str) -> dict:
        """
        Loads and returns a JSON dictionary from the specified log category.
        """
        file_path = self._get_log_file(category, suffix)
        if not file_path:
            raise FileNotFoundError(
                f"Missing log file: {self.log_dir / category / f'{self.base_name}_{suffix}.json'}"
            )
        return json.loads(file_path.read_text(encoding="utf-8"))

    def check_alignment(self) -> bool:
        """
        Check whether the feedback log aligns with quality evaluation sections.
        """
        try:
            quality_data = self.load_json("quality_log", f"v{self.version}")
            feedback_data = self.load_json("feedback_log", f"v{self.version+1}")

            quality_sections = set(quality_data.keys())
            feedback_sections = set(feedback_data.keys())

            aligned = quality_sections.issubset(feedback_sections)
            print(f"🧠 Controller evaluation: Alignment = {aligned}")
            return aligned

        except Exception as e:
            print(f"❌ ControllerAgent failed during alignment check: {e}")
            return False

    def request_retry(self) -> bool:
        """
        Determines if a retry should be triggered based on alignment failure.
        """
        aligned = self.check_alignment()
        if not aligned:
            self.retry_count += 1
            if self.retry_count > self.max_retries:
                print("🚫 Retry limit reached. Aborting.")
                return False
            print(f"🔁 Feedback misaligned – retry #{self.retry_count} requested.")
            return True
        return False

    def reset(self):
        """
        Resets retry counter (optional between iterations).
        """
        self.retry_count = 0
