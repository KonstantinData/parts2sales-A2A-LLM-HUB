import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock

from agents.controller_agent import ControllerAgent

class DummyAgent:
    def run(self, *args, **kwargs):
        return None

class TestControllerPromptValidation(unittest.TestCase):
    def test_invalid_prompt_stops_workflow(self):
        temp_dir = tempfile.TemporaryDirectory()
        try:
            prompt_path = Path(temp_dir.name) / "bad.yaml"
            prompt_path.write_text("version: '1.0'\nrole: r\nobjective: o\n")

            registry = {"dummy": MagicMock(spec=DummyAgent)}
            controller = ControllerAgent(registry, log_dir=Path(temp_dir.name))
            steps = [
                {
                    "type": "dummy",
                    "params": {"prompt_path": prompt_path, "base_name": "b", "iteration": 0},
                }
            ]
            with self.assertRaises(ValueError):
                controller.run(steps, workflow_id="wf_test")

            registry["dummy"].run.assert_not_called()

            log_file = Path(temp_dir.name) / "wf_test.jsonl"
            with open(log_file, "r", encoding="utf-8") as f:
                events = [json.loads(line) for line in f]
            self.assertTrue(any(e["event_type"] == "error" for e in events))
        finally:
            temp_dir.cleanup()

if __name__ == "__main__":
    unittest.main()
