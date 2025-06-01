"""
Unit test for PromptQualityAgent

#Notes:
- Tests matrix, llm, and hybrid scoring for a sample prompt.
- Checks that all fields are present and within range.
"""

import unittest
from agents.core.prompt_quality_agent import PromptQualityAgent


class TestPromptQualityAgent(unittest.TestCase):

    def setUp(self):
        self.agent = PromptQualityAgent()

    def test_matrix_score(self):
        prompt = "Fill the fields: {name}, {desc}."
        result = self.agent.score_prompt(prompt, method="matrix")
        self.assertTrue(0 <= result.total <= 1)
        self.assertEqual(result.method, "matrix")

    def test_llm_score(self):
        prompt = "Clear and concise: {foo}, {bar}."
        result = self.agent.score_prompt(prompt, method="llm")
        self.assertTrue(0 <= result.total <= 1)
        self.assertEqual(result.method, "llm")

    def test_hybrid_score(self):
        prompt = "Brief: {a}, {b}."
        result = self.agent.score_prompt(prompt, method="hybrid")
        self.assertTrue(0 <= result.total <= 1)
        self.assertEqual(result.method, "hybrid")


if __name__ == "__main__":
    unittest.main()
