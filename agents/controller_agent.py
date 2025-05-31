# controller_agent.py
"""
Controller Agent - Professional Version

Purpose:
--------
- Validates if prompt improvements align with provided feedback using GPT-4.
- Logs decisions with timestamp and explanations.
- Controls retry logic with maximum retry limits.
- Persistently tracks retry attempts based on saved logs.
"""

import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI


class ControllerAgent:
    def __init__(
        self,
        base_name: str,
        version: int,
        log_dir: Path,
        client: OpenAI,
        max_retries: int = 3,
    ):
        self.base_name = base_name
        self.version = version
        self.log_dir = log_dir
        self.control_log_dir = log_dir / "control_log"
        self.control_log_dir.mkdir(parents=True, exist_ok=True)

        self.client = client
        self.max_retries = max_retries

        # Persistent retry count laden
        self.retry_count = self._load_retry_count()

    def _load_retry_count(self) -> int:
        """Liest Control-Logs und zählt vorhandene Retries für diese Version."""
        retry_count = 0
        for file in self.control_log_dir.glob(
            f"{self.base_name}_v{self.version}_*.json"
        ):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                if data.get("retry_requested", False):
                    retry_count += 1
            except Exception:
                continue
        return retry_count

    def check_alignment(self, prompt_text: str, feedback: dict) -> bool:
        """
        Perform an alignment check by asking GPT-4 if the improved prompt
        sufficiently addresses all feedback points.

        Returns:
            bool: True if aligned, False otherwise.
        """
        system_prompt = (
            "You are a prompt evaluation expert. Given a prompt and feedback, "
            "assess if the prompt improvements sufficiently address the feedback. "
            "Respond succinctly with 'yes' or 'no', followed by a brief explanation."
        )
        user_prompt = (
            f"Improved Prompt:\n{prompt_text}\n\n"
            f"Feedback:\n{json.dumps(feedback, indent=2)}\n\n"
            "Does the improved prompt sufficiently address the feedback? "
            "Answer with 'yes' or 'no' and provide a brief explanation."
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=150,
            )
            answer = response.choices[0].message.content.strip().lower()
            aligned = answer.startswith("yes")

            self._log_decision(aligned, answer)
            return aligned

        except Exception as e:
            self._log_decision(
                False, f"Alignment check failed due to API error: {str(e)}"
            )
            return False

    def _log_decision(self, aligned: bool, explanation: str):
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        log_data = {
            "base_name": self.base_name,
            "version": self.version,
            "timestamp": timestamp,
            "aligned": aligned,
            "explanation": explanation,
            "retry_requested": False,
        }
        log_path = (
            self.control_log_dir / f"{self.base_name}_v{self.version}_{timestamp}.json"
        )
        log_path.write_text(json.dumps(log_data, indent=2, ensure_ascii=False))
        print(f"📝 Control log saved: {log_path.name}")

    def request_retry(self) -> bool:
        """
        Determines if a retry should be requested based on retry count and max limit.

        Returns:
            bool: True if retry allowed, False if max retries reached.
        """
        if self.retry_count >= self.max_retries:
            print(
                f"⚠️ Max retries ({self.max_retries}) reached for {self.base_name} v{self.version}."
            )
            return False

        self.retry_count += 1
        print(
            f"🔁 Retry #{self.retry_count} requested for {self.base_name} v{self.version}."
        )
        # Log the retry request
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        log_data = {
            "base_name": self.base_name,
            "version": self.version,
            "timestamp": timestamp,
            "retry_requested": True,
            "retry_count": self.retry_count,
        }
        log_path = (
            self.control_log_dir
            / f"{self.base_name}_v{self.version}_retry_{timestamp}.json"
        )
        log_path.write_text(json.dumps(log_data, indent=2, ensure_ascii=False))
        print(f"📝 Retry log saved: {log_path.name}")

        return True
