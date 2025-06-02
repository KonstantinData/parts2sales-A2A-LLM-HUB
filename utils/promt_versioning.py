"""
prompt_versioning.py

Utility module for semantic version and stage management of prompt templates
in the agentic article-to-action workflow.

Usage:
- Parse stage and semantic version from prompt filenames
- Calculate the next lifecycle stage, with option to skip 'config'
- Bump semantic versions (patch/minor/major)
- Resolve target directories by stage
- Promote prompt files by renaming/moving with version bump

Notes:
- Supports prompt stages: raw, templ, config, active
- Designed for seamless prompt lifecycle automation
- Uses regex and packaging.version for robust parsing and versioning
"""

import re
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
        new_version = Version(f"{v.major}.{v.minor}.{v.micro + 1}")
    elif mode == "minor":
        new_version = Version(f"{v.major}.{v.minor + 1}.0")
    elif mode == "major":
        new_version = Version(f"{v.major + 1}.0.0")
    else:
        raise ValueError(f"Unknown bump mode: {mode}")
    return str(new_version)


def next_stage(current_stage: str, allow_skip_config: bool = True) -> str:
    """
    Determine the next lifecycle stage.
    If allow_skip_config is True, skips 'config' stage in promotion.
    """
    if current_stage not in STAGES:
        raise ValueError(f"Unknown stage: {current_stage}")
    idx = STAGES.index(current_stage)
    if idx == len(STAGES) - 1:
        return current_stage  # already at 'active'
    if allow_skip_config and STAGES[idx + 1] == "config":
        return STAGES[idx + 2] if idx + 2 < len(STAGES) else STAGES[-1]
    else:
        return STAGES[idx + 1]


def resolve_target_dir(stage: str, current_path: Path) -> Path:
    """
    Resolve the destination directory path based on the stage and current path.
    Adjust ROOT and folder naming to match project conventions.
    """
    ROOT = current_path.parents[3]  # Adjust depending on your directory depth

    # Example directory mapping per stage
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
        raise ValueError(f"Unknown stage for target directory: {stage}")


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

    if next_stg == "active" and stage != "active":
        new_version = bump_version(version, mode="major")
    else:
        new_version = bump_version(version, mode="patch")

    new_name = re.sub(rf"_{stage}_v{version}", f"_{next_stg}_v{new_version}", filename)
    target_dir = resolve_target_dir(next_stg, current_path)
    target_dir.mkdir(parents=True, exist_ok=True)
    new_path = target_dir / new_name

    current_path.rename(new_path)
    return new_path
