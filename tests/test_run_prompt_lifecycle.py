import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from cli.run_prompt_lifecycle import evaluate_and_improve_prompt


class TestLifecycleDecision(unittest.TestCase):
    def _make_temp_prompt(self):
        temp_dir = tempfile.TemporaryDirectory()
        path = Path(temp_dir.name) / "feature_setup_raw_v0.0.1.yaml"
        path.write_text("version: '0.0.1'\n")
        return temp_dir, path

    def test_continue_when_not_passed(self):
        temp_dir, path = self._make_temp_prompt()
        try:
            pq_event = MagicMock()
            pq_event.payload = {"passed": False, "pass_threshold": 0.9, "score": 0.5, "feedback": []}
            with patch("cli.run_prompt_lifecycle.PromptQualityAgent") as MockPQ, \
                patch("cli.run_prompt_lifecycle.PromptImprovementAgent") as MockPI, \
                patch("cli.run_prompt_lifecycle.JsonlEventLogger") as MockLogger:
                MockPQ.return_value.run.return_value = pq_event
                MockPI.return_value.run.return_value = MagicMock(meta={"updated_path": str(path)})
                MockLogger.return_value.log_event.return_value = None

                evaluate_and_improve_prompt(path, openai_client=None)

                MockPI.return_value.run.assert_called_once()
        finally:
            temp_dir.cleanup()

    def test_stop_when_passed(self):
        temp_dir, path = self._make_temp_prompt()
        try:
            pq_event = MagicMock()
            pq_event.payload = {"passed": True, "pass_threshold": 0.9, "score": 0.95, "feedback": []}
            with patch("cli.run_prompt_lifecycle.PromptQualityAgent") as MockPQ, \
                patch("cli.run_prompt_lifecycle.PromptImprovementAgent") as MockPI, \
                patch("cli.run_prompt_lifecycle.JsonlEventLogger") as MockLogger:
                MockPQ.return_value.run.return_value = pq_event
                MockLogger.return_value.log_event.return_value = None
                evaluate_and_improve_prompt(path, openai_client=None)
                MockPI.return_value.run.assert_not_called()
        finally:
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
