import json
import re

_LINE_PREFIX_RE = re.compile(r"^\s*(?:-\s*|\d+\.\s*)", re.MULTILINE)


def _strip_bullet_prefixes(text: str) -> str:
    """Remove leading bullet or numbering prefixes from each line."""
    return _LINE_PREFIX_RE.sub("", text)


def extract_json_array_from_response(response: str) -> list:
    """
    Extracts a JSON array from an LLM response string by identifying the first array block,
    or, if not found, extracts arrays from within JSON objects (with key preference).
    Raises ValueError if nothing valid found.
    """
    if not isinstance(response, str):
        raise ValueError("LLM response is not a string.")

    cleaned = _strip_bullet_prefixes(response.strip())
    if not cleaned:
        raise ValueError("LLM response is empty.")

    # Abort early if the response looks like a clarification or error message.
    if not cleaned.lstrip().startswith("[") and not cleaned.lstrip().startswith("{"):
        raise ValueError(
            f"LLM response is not JSON but natural language: {cleaned[:80]}"
        )

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

    # Fallback: try to parse entire response as JSON and extract arrays under preferred keys.
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, list):
            return obj
        if isinstance(obj, dict):
            # Preferred keys for arrays (customize as needed)
            preferred_keys = [
                "companies",
                "interestedCompanies",
                "company_names",
                "results",
                "products",
                "items",
                "data",
            ]
            for key in preferred_keys:
                if key in obj and isinstance(obj[key], list):
                    return obj[key]
            arrays = [v for v in obj.values() if isinstance(v, list)]
            if len(arrays) == 1:
                return arrays[0]
            elif len(arrays) > 1:
                raise ValueError(
                    f"Multiple arrays found in response object: keys = {[k for k,v in obj.items() if isinstance(v, list)]}. Specify expected key."
                )
    except json.JSONDecodeError:
        pass

    raise ValueError(f"No JSON array found in the response. Start: {cleaned[:80]}")
