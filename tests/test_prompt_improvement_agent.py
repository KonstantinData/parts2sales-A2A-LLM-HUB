import unittest
import tempfile
from pathlib import Path

from agents.prompt_improvement_agent import PromptImprovementAgent


class DummyLLM:
    class Response:
        def __init__(self, content: str):
            self.choices = [type("Choice", (), {"message": {"content": content}})]

    def __init__(self, content: str = "improved"):
        self.content = content

    def chat_completion(self, *args, **kwargs):
        return self.Response(self.content)


class TestPromptImprovementAgent(unittest.TestCase):
    def test_patch_version_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            prompt_path = tmp / "sample_raw_v0.0.1.yaml"
            prompt_path.write_text("version: '0.0.1'\nrole: r\nobjective: o\n")

            agent = PromptImprovementAgent(
                improvement_strategy="LLM",
                openai_client=DummyLLM("role: r\nobjective: o\n"),
                log_dir=tmp,
            )
            event = agent.run(prompt_path, prompt_path.stem, 0, workflow_id="wf1")

            new_path = tmp / "sample_raw_v0.0.2.yaml"
            self.assertTrue(new_path.exists())
            new_content = new_path.read_text()
            self.assertIn("version: '0.0.2'", new_content)

            self.assertEqual(event.meta.get("updated_path"), str(new_path))
            self.assertEqual(event.meta.get("old_version"), "0.0.1")
            self.assertEqual(event.meta.get("new_version"), "0.0.2")


if __name__ == "__main__":
    unittest.main()
