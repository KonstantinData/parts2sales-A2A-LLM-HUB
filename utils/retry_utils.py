# utils/retry_utils.py

from typing import Optional
from pydantic import BaseModel


class RetryStatus(BaseModel):
    retry_allowed: bool = False
    retry_count: int = 0
    retry_reason: Optional[str] = None

    def increment(self, reason: str):
        self.retry_allowed = True
        self.retry_count += 1
        self.retry_reason = reason
