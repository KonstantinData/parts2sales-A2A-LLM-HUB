"""
scoring_matrix_loader.py

Purpose : Loads a scoring matrix given a ScoringMatrixType enum value.
Version : 1.1.0
Author  : Konstantin & AI Copilot
Notes   :
- Loads from config/scoring/{type}_scoring_matrix.py and expects 'SCORING_MATRIX' dict.
- Ensures matrix type exists and is valid.
- Extensible for future types.
"""

from utils.scoring_matrix_types import ScoringMatrixType
import importlib.util
from pathlib import Path
from typing import Dict

SCORING_MATRIX_ROOT = Path(__file__).resolve().parent.parent / "config" / "scoring"


def load_scoring_matrix(matrix_type: ScoringMatrixType) -> Dict:
    """
    Loads the scoring matrix for the given matrix type.

    Args:
        matrix_type (ScoringMatrixType): The type of scoring matrix to load.

    Returns:
        dict: The scoring matrix.

    Raises:
        FileNotFoundError: If the scoring matrix file is missing.
        AttributeError: If the scoring matrix file does not define SCORING_MATRIX.
    """
    filename = f"{matrix_type.value}_scoring_matrix.py"
    path = SCORING_MATRIX_ROOT / filename
    if not path.exists():
        raise FileNotFoundError(f"Scoring matrix file not found: {path}")

    spec = importlib.util.spec_from_file_location("scoring_matrix_mod", str(path))
    scoring_matrix_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scoring_matrix_mod)
    if not hasattr(scoring_matrix_mod, "SCORING_MATRIX"):
        raise AttributeError(f"{path} does not expose SCORING_MATRIX dict.")
    return scoring_matrix_mod.SCORING_MATRIX
