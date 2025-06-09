"""
utils/time_utils.py

Purpose : Utility functions for timezone-aware timestamps and filenames.
Version : 2.0.0
Author  : Konstantin Milonas with Agentic AI Copilot support
"""

from datetime import datetime, timezone, timedelta


def cet_now():
    """Return current time in CET (Central European Time) with timezone info."""
    return datetime.now(timezone(timedelta(hours=1), name="CET"))


def timestamp_for_filename():
    """Return a safe string timestamp for filenames (YYYY-MM-DDTHH-MM-SS)."""
    return cet_now().strftime("%Y-%m-%dT%H-%M-%S")
