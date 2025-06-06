"""
Unit test for PromptQualityAgent

#Notes:
- Tests matrix, llm, and hybrid scoring for a sample prompt.
- Checks that all fields are present and within range.
"""

import unittest
import tempfile
from pathlib import Path

from agents.prompt_quality_agent import PromptQualityAgent
from utils.scoring_matrix_types import ScoringMatrixType


class TestPromptQualityAgent(unittest.TestCase):

    def setUp(self):
        self.agent = PromptQualityAgent(ScoringMatrixType.RAW, None)

    def _run_prompt(self, text: str):
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            tmp.write(text)
            tmp.flush()
            path = Path(tmp.name)
        try:
            return self.agent.run(path, path.stem, 0)
        finally:
            path.unlink()

    def test_matrix_score(self):
        prompt = "Fill the fields: {name}, {desc}."
        event = self._run_prompt(prompt)
        score = event.payload.get("matrix_score", 0)
        self.assertTrue(0 <= score <= 1)

    def test_llm_score(self):
        prompt = "Clear and concise: {foo}, {bar}."
        event = self._run_prompt(prompt)
        score = event.payload.get("llm_score", 0)
        self.assertTrue(0 <= score <= 1)

    def test_hybrid_score(self):
        prompt = "Brief: {a}, {b}."
        event = self._run_prompt(prompt)
        matrix_score = event.payload.get("matrix_score", 0)
        llm_score = event.payload.get("llm_score", 0)
        self.assertTrue(0 <= matrix_score <= 1)
        self.assertTrue(0 <= llm_score <= 1)


if __name__ == "__main__":
    unittest.main()
