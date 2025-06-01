import hashlib, json

def cache_decorator(func):
    _cache = {}
    def wrapper(*args, **kwargs):
        key = hashlib.sha256(json.dumps(args, sort_keys=True, default=str).encode()).hexdigest()
        if key in _cache:
            return _cache[key]
        result = func(*args, **kwargs)
        _cache[key] = result
        return result
    return wrapper

@cache_decorator
def llm_judge(prompt: str) -> float:
    # Hier LLM Call einbauen
    # Dummy: immer 0.95
    return 0.95
