"""Statement use case."""

from datetime import date
from decimal import Decimal

from services.limits.domain.limits import Entry
from services.limits.infrastructure import memory_store
from services.shared.errors import ValidationFailed


def statement(customer_id: str, start: date, end: date) -> tuple[list[Entry], Decimal]:
    """Rules 9-10: inclusive range, date-ascending, approval order within a day."""
    if start > end:
        raise ValidationFailed("from, to tarihinden sonra olamaz")
    with memory_store.lock:
        items = [e for e in memory_store.entries.get(customer_id, []) if start <= e.occurred_on <= end]
    items.sort(key=lambda e: e.occurred_on)  # stable sort keeps approval order
    total = sum((e.amount for e in items), Decimal("0"))
    return items, total
