"""
Prompt Loader

Version: 2.0.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Handles loading, saving, and versioning of prompt files.
Used by all agents for prompt I/O and template promotion.
"""

import os
import shutil
import yaml
from utils.prompt_versioning import bump_version


def load_prompt_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_prompt_file_with_new_version(original_path: str, prompt_data: dict) -> str:
    new_path = bump_version(original_path, target_layer="01-template")
    with open(new_path, "w", encoding="utf-8") as f:
        yaml.dump(prompt_data, f, allow_unicode=True)
    return new_path


def file_exists(path: str) -> bool:
    return os.path.isfile(path)


def move_to_template_layer(path: str) -> None:
    new_path = bump_version(path, target_layer="01-template")
    shutil.move(path, new_path)
