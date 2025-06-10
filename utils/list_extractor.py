# utils/list_extractor.py


def extract_list_anywhere(obj, key_candidates):
    """
    Durchsucht beliebig verschachtelte dict/list-Objekte nach einer Liste unter einem der angegebenen Schlüssel.
    Gibt die erste gefundene Liste zurück oder None.
    """
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in key_candidates:
            if k in obj and isinstance(obj[k], list):
                return obj[k]
        for v in obj.values():
            found = extract_list_anywhere(v, key_candidates)
            if found is not None:
                return found
    return None
