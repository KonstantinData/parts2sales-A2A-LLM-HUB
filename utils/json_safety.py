# utils/json_safety.py

import json


def extract_json_array_from_response(response: str) -> list:
    """
    Extracts a JSON array from an LLM response string by identifying the first array block.
    Strips any surrounding text or explanations. Raises an error if extraction fails.
    """
    if not isinstance(response, str):
        raise ValueError("LLM response is not a string.")

    cleaned = response.strip()
    if not cleaned:
        raise ValueError("LLM response is empty.")

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON array found in the response.")

    json_snippet = cleaned[start : end + 1]

    try:
        parsed = json.loads(json_snippet)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not decode extracted JSON array: {e}")

    if not isinstance(parsed, list):
        raise ValueError("Parsed content is not a JSON list.")

    return parsed
