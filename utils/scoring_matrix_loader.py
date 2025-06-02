"""
scoring_matrix_loader.py

Purpose : Loads and validates scoring matrices for all agent types (feature, usecase, industry, contact) from config/scoring.
Version : 0.1.0
Author  : Konstantin & AI Copilot
Notes   :
- Centralizes all scoring matrix loads to avoid duplicate logic.
- Handles missing/invalid files and warns with clear error messages.
- Extendible for new matrices.
"""

from pathlib import Path
from typing import Dict, Any, Optional

SCORING_MATRIX_FILES = {
    "feature": "feature_scoring_matrix.py",
    "usecase": "usecase_scoring_matrix.py",
    "industry": "industry_scoring_matrix.py",
    "contact": "contact_scoring_matrix.py",
}


def load_scoring_matrix(matrix_type: str) -> Optional[Dict[str, Any]]:
    from importlib.util import spec_from_file_location, module_from_spec

    filename = SCORING_MATRIX_FILES.get(matrix_type)
    if not filename:
        raise ValueError(f"Unknown matrix_type: {matrix_type}")
    matrix_path = Path("config/scoring") / filename
    if not matrix_path.exists():
        print(f"[WARN] Scoring matrix file not found: {matrix_path}")
        return None

    spec = spec_from_file_location(matrix_type, str(matrix_path))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    # The exported variable should always be named e.g. FEATURE_SCORING_MATRIX
    for var in dir(module):
        if var.endswith("_SCORING_MATRIX"):
            return getattr(module, var)
    print(f"[WARN] No scoring matrix dict found in {filename}")
    return None


# Usage example:
# matrix = load_scoring_matrix("feature")
