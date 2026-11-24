"""In-memory storage for limits, daily usage and approved transactions."""

import threading
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

# Guards every read-check-write sequence so authorize is atomic.
lock = threading.RLock()


@dataclass(frozen=True)
class CustomerLimits:
    daily_limit: Decimal
    per_transfer_limit: Decimal


@dataclass(frozen=True)
class Entry:
    occurred_on: date
    amount: Decimal
    description: str | None


limits: dict[str, CustomerLimits] = {}
usage: dict[tuple[str, date], Decimal] = {}
entries: dict[str, list[Entry]] = {}


def reset() -> None:
    with lock:
        limits.clear()
        usage.clear()
        entries.clear()
