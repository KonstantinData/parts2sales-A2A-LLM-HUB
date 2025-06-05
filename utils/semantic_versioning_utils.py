from __future__ import annotations

"""Utility helpers for semantic version management used across the project.

This module centralizes logic for bumping versions and updating the ``version``
field inside YAML prompt files.  Keeping this logic in one place avoids
duplicated regex code throughout the agents and CLI.
"""

from pathlib import Path
from packaging.version import Version, InvalidVersion
import re
import yaml


def bump(version: str, level: str = "patch") -> str:
    """Return a new version string bumped at the given level."""
    # Parse version via ``packaging`` for robustness (e.g. ``1.2.3`` -> parts)
    try:
        v = Version(version)
    except InvalidVersion as ex:
        raise ValueError(f"Invalid version string: {version}") from ex

    # Normalise the level argument so case does not matter
    level = level.lower()
    if level == "patch":
        return f"{v.major}.{v.minor}.{v.micro + 1}"
    if level == "minor":
        return f"{v.major}.{v.minor + 1}.0"
    if level == "major":
        return f"{v.major + 1}.0.0"
    # ``level`` was not recognised
    raise ValueError(f"Unknown bump level: {level}")


# Backwards compatibility
bump_version = bump


def parse_version_from_yaml(path: Path) -> str:
    """Return the ``version`` field from a YAML file or ``'0.0.0'`` if missing."""

    # ``yaml.safe_load`` returns ``None`` when the file is empty
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Extract version as string so callers don't need to handle ``None``
    return str(data.get("version", "0.0.0"))


def update_version_in_yaml_string(content: str, new_version: str) -> str:
    """Return ``content`` with the ``version`` field replaced/added."""

    # Regex matches e.g. ``version: '1.2.3'`` anywhere in the YAML
    version_line_re = re.compile(r"^version:\s*.+$", flags=re.MULTILINE)
    new_line = f"version: '{new_version}'"

    if version_line_re.search(content):
        # Replace existing version line
        return version_line_re.sub(new_line, content)

    # If the version field was missing prepend it at the top
    return f"{new_line}\n{content}"


def update_version_in_yaml_file(path: Path, new_version: str) -> None:
    """In-place update of the ``version`` field in ``path``."""

    with path.open("r", encoding="utf-8") as f:
        content = f.read()

    updated = update_version_in_yaml_string(content, new_version)

    with path.open("w", encoding="utf-8") as f:
        f.write(updated)
