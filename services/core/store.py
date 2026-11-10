"""In-memory persistence for Aurora Core (workshop only, not for production).

`reset()` is part of the public test API (see docs/ENGINEERING-HANDBOOK.md).
Do not remove it.
"""

accounts: dict[str, dict] = {}
transfers: dict[str, dict] = {}
idempotency: dict[str, dict] = {}


def reset() -> None:
    accounts.clear()
    transfers.clear()
    idempotency.clear()
