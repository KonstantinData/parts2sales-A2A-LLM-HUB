import os
import unittest
import tempfile
from pathlib import Path

from agents.llm_prompt_scorer import LLMPromptScorer


class TestLLMPromptScorerEnvThreshold(unittest.TestCase):
    def setUp(self):
        self.matrix = {
            "a": {"weight": 1.0, "required_snippet": "a", "feedback": "f"},
            "b": {"weight": 1.0, "required_snippet": "b", "feedback": "f"},
        }
        self.scorer = LLMPromptScorer(self.matrix)

    def test_custom_threshold(self):
        os.environ["THRESHOLD"] = "0.4"
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            tmp.write("only a present")
            tmp.flush()
            path = Path(tmp.name)
        try:
            event = self.scorer.run(path, "t", 0)
        finally:
            path.unlink()
            del os.environ["THRESHOLD"]
        self.assertEqual(event.payload["pass_threshold"], 0.4)
        self.assertTrue(event.payload["passed"])


if __name__ == "__main__":
    unittest.main()
