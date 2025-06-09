import pytest
from utils.json_safety import extract_json_array_from_response


def test_extract_with_bullet_lines():
    text = """[
- "A",
- "B"
]"""
    assert extract_json_array_from_response(text) == ["A", "B"]


def test_extract_with_numbered_lines():
    text = """[
1. "A",
2. "B"
]"""
    assert extract_json_array_from_response(text) == ["A", "B"]


def test_extract_with_mixed_inline_bullet():
    text = '["A",\n- "B"]'
    assert extract_json_array_from_response(text) == ["A", "B"]
