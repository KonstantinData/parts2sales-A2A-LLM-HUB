# utils/json_safety.py

import json
import re


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

    # Try to find the first JSON array in the string using regex.
    array_match = re.search(r"\[[\s\S]*?\]", cleaned)
    if array_match:
        json_snippet = array_match.group(0)
        try:
            parsed = json.loads(json_snippet)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not decode extracted JSON array: {e}")
        if isinstance(parsed, list):
            return parsed
        raise ValueError("Parsed content is not a JSON list.")

    # Fallback: try to parse entire response as JSON and extract the first list.
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, list):
            return obj
        if isinstance(obj, dict):
            for value in obj.values():
                if isinstance(value, list):
                    return value
    except json.JSONDecodeError:
        pass

    raise ValueError(f"No JSON array found in the response. Start: {cleaned[:80]}")
