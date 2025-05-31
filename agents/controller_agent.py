# controller_agent.py
"""
Controller Agent for Coordinating Prompt Quality and Improvement

Purpose:
--------
This agent acts as a central coordinator between the prompt quality assessment,
prompt improvement logic, and execution. It ensures that prompt feedback aligns
with quality findings both structurally and semantically, and that actual improvements
occur before execution.

Key Features:
-------------
1. Loads and verifies log files (quality, feedback, prompt).
2. Evaluates feedback alignment using OpenAI's GPT (semantic validation).
3. Detects whether a prompt has meaningfully changed.
4. Implements retry logic if improvement fails or misaligns.

Environment:
------------
- Requires `openai` and `python-dotenv`
- Expects an `.env` file containing: OPENAI_API_KEY=sk-...
"""

import os
import json
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import openai

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


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
        Helper function to construct a valid path to a log file if it exists.
        """
        file_path = self.log_dir / category / f"{self.base_name}_{suffix}.json"
        return file_path if file_path.exists() else None

    def load_json(self, category: str, suffix: str) -> dict:
        """
        Loads a JSON file from the given log category and suffix.
        """
        file_path = self._get_log_file(category, suffix)
        if not file_path:
            raise FileNotFoundError(
                f"Missing log file: {self.log_dir / category / f'{self.base_name}_{suffix}.json'}"
            )
        return json.loads(file_path.read_text(encoding="utf-8"))

    def check_alignment(self) -> bool:
        """
        Checks whether the feedback addresses the quality issues:
        - Structurally: all quality sections are covered in feedback
        - Semantically: each feedback section addresses the concern using OpenAI GPT
        """
        try:
            quality_data = self.load_json("quality_log", f"v{self.version}")
            feedback_data = self.load_json("feedback_log", f"v{self.version + 1}")

            quality_keys = set(quality_data.keys())
            feedback_keys = set(feedback_data.keys())

            # Step 1: Structural alignment
            key_alignment = quality_keys.issubset(feedback_keys)

            # Step 2: Semantic validation using OpenAI
            semantic_valid = self.evaluate_feedback_semantically(
                quality_data, feedback_data
            )

            print(
                f"🧠 Alignment Check: Keys OK = {key_alignment}, Semantics OK = {semantic_valid}"
            )
            return key_alignment and semantic_valid

        except Exception as e:
            print(f"❌ Alignment check failed: {e}")
            return False

    def evaluate_feedback_semantically(
        self, quality_data: dict, feedback_data: dict
    ) -> bool:
        """
        Iterates over each feedback item and validates it with OpenAI's language model.
        """
        for section, issue in quality_data.items():
            if section not in feedback_data:
                print(f"⚠️ Missing feedback for section '{section}'")
                return False
            feedback = feedback_data[section]
            prompt = self.build_openai_prompt(issue, feedback)
            if not self.evaluate_with_openai(prompt):
                print(f"⚠️ Weak or unrelated feedback in section '{section}'")
                return False
        return True

    def build_openai_prompt(self, issue: str, feedback: str) -> str:
        """
        Constructs a prompt to ask OpenAI whether the feedback resolves the quality issue.
        """
        return (
            f"Here is a prompt quality concern:\n\n"
            f"{issue}\n\n"
            f"Here is the proposed feedback to improve it:\n\n"
            f"{feedback}\n\n"
            f"Does this feedback clearly address and resolve the concern? Reply with YES or NO."
        )

    def evaluate_with_openai(self, prompt: str) -> bool:
        """
        Sends prompt to OpenAI's chat model and returns True if response is YES.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            result = response.choices[0].message["content"].strip().upper()
            return "YES" in result
        except Exception as e:
            print(f"❌ OpenAI call failed: {e}")
            return False

    def prompt_has_significant_changes(self) -> bool:
        """
        Compares the current prompt version with the previous one.
        Returns True if a meaningful change occurred.
        """
        try:
            previous = self.load_json("prompt_log", f"v{self.version}")[
                "content"
            ].strip()
            current = self.load_json("prompt_log", f"v{self.version + 1}")[
                "content"
            ].strip()
            changed = previous != current
            print(f"🔍 Prompt changed: {changed}")
            return changed
        except Exception as e:
            print(f"❌ Change detection failed: {e}")
            return False

    def request_retry(self) -> bool:
        """
        Returns True if alignment failed or no meaningful changes were made,
        and retry attempts are still available.
        """
        aligned = self.check_alignment()
        changed = self.prompt_has_significant_changes()

        if not aligned or not changed:
            self.retry_count += 1
            if self.retry_count > self.max_retries:
                print("🚫 Retry limit exceeded.")
                return False
            print(f"🔁 Retry #{self.retry_count} triggered.")
            return True

        return False

    def reset(self):
        """
        Resets the retry count (can be used between cycles).
        """
        self.retry_count = 0
