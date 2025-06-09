import json


def extract_json_array_from_response(response: str) -> list:
    """
    Parses a JSON array, an object with a top-level array,
    or a dict of arrays (all lists will be concatenated).
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
        # Known standard keys (features, companies, etc)
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
        # Sonderfall: dict mit nur Listen als Werte
        if all(isinstance(v, list) for v in parsed.values()) and len(parsed) > 0:
            combined = []
            for v in parsed.values():
                combined.extend(v)
            return combined
    raise ValueError("No valid array found in LLM response.")
