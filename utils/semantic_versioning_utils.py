
from packaging.version import Version

def bump_patch(version_str: str) -> str:
    v = Version(version_str)
    return f"{v.major}.{v.minor}.{v.micro + 1}"

def bump_minor(version_str: str) -> str:
    v = Version(version_str)
    return f"{v.major}.{v.minor + 1}.0"

def bump_major(version_str: str) -> str:
    v = Version(version_str)
    return f"{v.major + 1}.0.0"

def bump(version_str: str, mode: str = "patch") -> str:
    if mode == "patch":
        return bump_patch(version_str)
    elif mode == "minor":
        return bump_minor(version_str)
    elif mode == "major":
        return bump_major(version_str)
    else:
        raise ValueError(f"Unknown bump mode: {mode}")
