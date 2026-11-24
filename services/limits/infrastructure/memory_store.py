"""In-memory storage for limits, daily usage and approved transactions.

Access collections as module attributes at call time; `services.limits.store` aliases
this same module object.
"""

import threading
from datetime import date
from decimal import Decimal

from services.limits.domain.limits import CustomerLimits, Entry

# Guards every read-check-write sequence so authorize is atomic.
lock = threading.RLock()

limits: dict[str, CustomerLimits] = {}
usage: dict[tuple[str, date], Decimal] = {}
entries: dict[str, list[Entry]] = {}


def reset() -> None:
    with lock:
        limits.clear()
        usage.clear()
        entries.clear()
