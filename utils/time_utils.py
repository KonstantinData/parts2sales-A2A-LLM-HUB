"""
Time Utilities

Version: 2.0.0
Author: Konstantin Milonas with Agentic AI Copilot support

Purpose:
Provides timezone-aware timestamps for event logging and filenames.
Standardized for CET and ISO format usage across all agents and logs.
"""

from datetime import datetime, timezone, timedelta


def cet_now() -> str:
    cet_offset = timedelta(
        hours=2
    )  # adjust for CET/CEST manually if DST logic not included
    return (datetime.utcnow().replace(tzinfo=timezone.utc) + cet_offset).isoformat()


def timestamp_for_filename() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
