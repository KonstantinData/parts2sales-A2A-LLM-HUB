"""
scoring_matrix_types.py

Purpose : Enum for all allowed scoring matrix types (lifecycle and task-specific)
Version : 1.0.0
Author  : Konstantin & AI Copilot
Notes   :
- Unified type for matrix-based quality evaluation (raw, template, feature, usecase, industry, company, contact)
- Used by loader, agents, and controller for type safety and consistency
"""

from enum import Enum


class ScoringMatrixType(Enum):
    RAW = "raw"
    TEMPLATE = "template"
    FEATURE = "feature"
    USECASE = "usecase"
    INDUSTRY = "industry"
    COMPANY = "company"
    CONTACT = "contact"
