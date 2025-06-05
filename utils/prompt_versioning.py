"""
prompt_versioning.py

Utility module for semantic version and stage management of prompt templates
in the agentic article-to-action workflow.
Version : 1.1.1
Author  : Konstantin’s AI Copilot
Notes   :
- Extracts stage/version from filenames and YAML
- Supports version bumping & stage progression
- Used by prompt lifecycle CLI & agent promotion
"""

import re
import yaml
from pathlib import Path
from packaging.version import Version, InvalidVersion

STAGES = ["raw", "templ", "config", "active"]


def extract_stage(filename: str) -> str:
    """
    Extract the lifecycle stage from the filename.
    E.g. 'feature_setup_templ_v0.2.0.yaml' -> 'templ'
    """
    pattern = r"_(raw|templ|config|active)_v\d+\.\d+\.\d+\.yaml$"
    match = re.search(pattern, filename)
    if not match:
        raise ValueError(f"Stage not found in filename: {filename}")
    return match.group(1)


def extract_version(filename: str) -> str:
    """
    Extract the semantic version string from the filename.
    E.g. 'feature_setup_templ_v0.2.0.yaml' -> '0.2.0'
    """
    pattern = r"_v(\d+\.\d+\.\d+)\.yaml$"
    match = re.search(pattern, filename)
    if not match:
        raise ValueError(f"Version not found in filename: {filename}")
    return match.group(1)


def parse_version_from_yaml(path: Path) -> str:
    """
    Parse the semantic version from a YAML file's content.
    Falls back to '0.0.0' if not found.
    """
    with path.open("r", encoding="utf-8") as file:
        content = yaml.safe_load(file)
    return str(content.get("version", "0.0.0"))


def bump_version(version_str: str, mode: str = "patch") -> str:
    """
    Increment the semantic version string by the given mode.
    Modes: 'patch', 'minor', 'major'
    """
    try:
        v = Version(version_str)
    except InvalidVersion:
        raise ValueError(f"Invalid version string: {version_str}")
    if mode == "patch":
        return f"{v.major}.{v.minor}.{v.micro + 1}"
    elif mode == "minor":
        return f"{v.major}.{v.minor + 1}.0"
    elif mode == "major":
        return f"{v.major + 1}.0.0"
    else:
        raise ValueError(f"Unknown bump mode: {mode}")


def next_stage(current_stage: str, allow_skip_config: bool = True) -> str:
    """
    Determine the next lifecycle stage.
    If allow_skip_config is True, skips 'config' stage in promotion.
    """
    if current_stage not in STAGES:
        raise ValueError(f"Unknown stage: {current_stage}")
    idx = STAGES.index(current_stage)
    if idx == len(STAGES) - 1:
        return current_stage
    if allow_skip_config and STAGES[idx + 1] == "config":
        return STAGES[idx + 2] if idx + 2 < len(STAGES) else STAGES[-1]
    return STAGES[idx + 1]


def resolve_target_dir(stage: str, current_path: Path) -> Path:
    """
    Resolve the destination directory path based on the stage and current path.
    Adjust ROOT and folder naming to match project conventions.
    """
    ROOT = current_path.parents[3]
    if stage in ["raw", "templ"]:
        return (
            ROOT
            / "prompts"
            / "00-templates"
            / "00-feature_setup"
            / f"feature_setup_{stage}"
        )
    elif stage == "config":
        return ROOT / "prompts" / "01-examples" / "00-feature_setup"
    elif stage == "active":
        return ROOT / "prompts" / "02-production" / "00-feature_setup"
    else:
        raise ValueError(f"Unknown stage: {stage}")


def promote_prompt(current_path: Path, allow_skip_config: bool = True) -> Path:
    """
    Promote a prompt file to the next stage with semantic version bump.
    - Parses stage and version from filename
    - Determines next stage with optional skipping of 'config'
    - Applies major bump only when moving to 'active'
    - Moves and renames the file to the correct folder with new version

    Returns the new Path of the promoted prompt.
    """
    filename = current_path.name
    stage = extract_stage(filename)
    version = extract_version(filename)
    next_stg = next_stage(stage, allow_skip_config=allow_skip_config)
    new_version = bump_version(
        version, mode="major" if next_stg == "active" else "patch"
    )
    new_name = re.sub(rf"_{stage}_v{version}", f"_{next_stg}_v{new_version}", filename)
    target_dir = resolve_target_dir(next_stg, current_path)
    target_dir.mkdir(parents=True, exist_ok=True)
    new_path = target_dir / new_name
    current_path.rename(new_path)
    return new_path


def clean_base_name(filename: str) -> str:
    """
    Remove version and stage suffix from filename.
    E.g. 'feature_setup_raw_v0.1.0.yaml' → 'feature_setup'
    """
    return re.sub(r"_(raw|templ|config|active)_v\d+\.\d+\.\d+\.yaml$", "", filename)


def improvement_filename(base_path: Path, iteration: int) -> Path:
    """
    Erzeugt einen konsistenten Pfad für verbesserte Prompts,
    z.B. 'feature_setup_raw_v0.1.0_improved_iter1.yaml' – auch wenn der Input schon improved ist.
    """
    name = base_path.name
    # Entferne '_improved_iterN' falls vorhanden (egal wie oft verbessert)
    cleaned = re.sub(r"_improved_iter\d+", "", name)
    # An cleaned Namen Suffix anhängen
    new_name = cleaned.replace(".yaml", f"_improved_iter{iteration}.yaml")
    return base_path.parent / new_name
