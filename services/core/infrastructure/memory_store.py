"""In-memory persistence for Aurora Core (workshop only, not for production).

Callers must access the collections as module attributes (``memory_store.accounts``) at call
time, never ``from ... import accounts``: test tooling swaps them on ``services.core.store``,
which is this same module object.
"""

import threading

# Serialises money movement so validate-then-write and idempotency checks are atomic.
lock = threading.RLock()

accounts: dict[str, dict] = {}
transfers: dict[str, dict] = {}
idempotency: dict[str, dict] = {}


def reset() -> None:
    from . import transfer_log

    with lock:
        accounts.clear()
        transfers.clear()
        idempotency.clear()
        transfer_log.reset()
