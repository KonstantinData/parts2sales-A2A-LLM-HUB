import json


def extract_json_array_from_response(response: str) -> list:
    """
    Parses a JSON array or a JSON object containing an array under any standard key.
    Robust against OpenAI response_format="json_object" outputs.
    """
    if not isinstance(response, str):
        raise ValueError("LLM response is not a string.")

    try:
        parsed = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}\nRaw: {response}")

    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        # Standard keys for arrays from all relevant tasks
        preferred_keys = [
            "features",
            "companies",
            "interestedCompanies",
            "company_names",
            "results",
            "products",
            "items",
            "data",
            "industries",
        ]
        for key in preferred_keys:
            if key in parsed and isinstance(parsed[key], list):
                return parsed[key]
    raise ValueError("No valid array found in LLM response.")
