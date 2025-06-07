import json
import os
import sys
from pathlib import Path
import pytest
from openai import OpenAIError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agents.llm_prompt_scorer import LLMPromptScorer

class FailingClient:
    def chat_completion(self, *args, **kwargs):
        raise OpenAIError("down")


def test_run_logs_error_and_returns_none(tmp_path):
    scoring_matrix = {"c1": {"description": "desc"}}
    scorer = LLMPromptScorer(scoring_matrix, openai_client=FailingClient(), log_dir=tmp_path)
    prompt_path = tmp_path / "prompt.txt"
    prompt_path.write_text("test")

    result = scorer.run(prompt_path, "base_v1", 0, workflow_id="wf")
    assert result is None

    log_file = tmp_path / "wf.jsonl"
    assert log_file.exists()
    logged = json.loads(log_file.read_text())
    assert logged["event_type"] == "error"
    assert logged["payload"] == {"reason": "LLM API unavailable"}
