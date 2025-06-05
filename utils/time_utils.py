"""
Time utilities with Central European Time (CET) defaults.

Provides a single function ``cet_now`` to obtain the current
``datetime`` in CET using Python's ``zoneinfo`` module.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

# Reuse this zoneinfo object across calls
CET_ZONE = ZoneInfo("Europe/Berlin")


def cet_now() -> datetime:
    """Return the current time in Central European Time (CET)."""
    return datetime.now(CET_ZONE)
