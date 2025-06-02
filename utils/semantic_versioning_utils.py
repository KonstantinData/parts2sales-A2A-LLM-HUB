"""
Semantic Versioning Utilities

Functions for parsing and bumping semantic versions following X.Y.Z pattern.
"""

import re

SEMVER_PATTERN = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def bump(version: str, mode: str = "patch") -> str:
    match = SEMVER_PATTERN.search(version)
    if not match:
        major, minor, patch = 0, 1, 0
    else:
        major, minor, patch = map(int, match.groups())

    if mode == "major":
        major += 1
        minor = 0
        patch = 0
    elif mode == "minor":
        minor += 1
        patch = 0
    elif mode == "patch":
        patch += 1
    else:
        raise ValueError(f"Unknown bump mode: {mode}")

    return f"{major}.{minor}.{patch}"
