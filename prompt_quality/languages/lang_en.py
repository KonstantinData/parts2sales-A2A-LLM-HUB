# lang_en.py

# Purpose:
# Define idiomatic, structural, lexical, and tonal patterns for English prompts
# and return not only boolean checks but also matched patterns for diagnostics


def idiomatic_expressions():
    return [
        "hit the ground running",
        "rule of thumb",
        "think outside the box",
        "back to the drawing board",
    ]


def action_keywords():
    return ["analyze", "create", "generate", "identify", "derive"]


def structure_keywords():
    return ["first", "then", "next", "finally", "in conclusion"]


def lexical_warnings():
    return ["analyze of", "do a derivation"]


def tone_blacklist():
    return ["whatever", "damn", "wtf"]


def is_actionable(text):
    found = [w for w in action_keywords() if w in text.lower()]
    return bool(found), found


def has_structure(text):
    found = [w for w in structure_keywords() if w in text.lower()]
    return len(found) >= 2, found


def has_idiom(text):
    found = [p for p in idiomatic_expressions() if p in text]
    return bool(found), found


def violates_lexical_rules(text):
    matches = [combo for combo in lexical_warnings() if combo in text]
    return len(matches) == 0, matches


def has_tone_issue(text):
    found = [term for term in tone_blacklist() if term in text.lower()]
    return len(found) == 0, found


def explanations():
    return {
        "grammar_check": "Fix grammar issues for clearer understanding.",
        "idiomatic_check": "Consider using idiomatic phrases for natural tone.",
        "task_clarity": "Clarify the instruction using action verbs like 'generate' or 'identify'.",
        "structure_check": "Add structure markers like 'first', 'then', 'finally' to guide the flow.",
        "lexical_fit": "Avoid awkward phrasing or uncommon combinations.",
        "tone_check": "Use a professional and neutral tone.",
        "translation_integrity": "Check that structure and intent match the source.",
    }
