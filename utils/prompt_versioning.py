"""
Prompt Versioning

Version: 2.0.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Handles semantic versioning of prompt files and promotes prompts
between layers (e.g., from raw to template).
"""

import os
import re
from pathlib import Path


def extract_version(filename: str) -> str:
    match = re.search(r"_v(\d+\.\d+\.\d+)", filename)
    if match:
        return match.group(1)
    return "0.0.0"


def bump_version(original_path: str, target_layer: str = None) -> str:
    path = Path(original_path)
    base_name = clean_base_name(path.name)
    current_version = extract_version(path.name)
    major, minor, patch = map(int, current_version.split("."))
    patch += 1
    new_version = f"{major}.{minor}.{patch}"
    new_filename = f"{base_name}_v{new_version}.yaml"

    if target_layer:
        new_dir = Path(path).parents[1] / target_layer
    else:
        new_dir = path.parent

    new_dir.mkdir(parents=True, exist_ok=True)
    return str(new_dir / new_filename)


def clean_base_name(filename: str) -> str:
    base = filename
    base = re.sub(r"_v\d+\.\d+\.\d+", "", base)
    base = re.sub(r"\.yaml$", "", base)
    return base
