"""Business rules for limits and statements (PRD section 4).

customer_id is validated at the HTTP layer only; functions here assume it is valid.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from . import store
from .store import CustomerLimits, Entry

DEFAULT_LIMITS = CustomerLimits(
    daily_limit=Decimal("10000.00"),
    per_transfer_limit=Decimal("5000.00"),
)

PER_TRANSFER_LIMIT_EXCEEDED = "PER_TRANSFER_LIMIT_EXCEEDED"
DAILY_LIMIT_EXCEEDED = "DAILY_LIMIT_EXCEEDED"


class ValidationError(Exception):
    """Invalid input; rendered as HTTP 422 VALIDATION_ERROR."""


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str | None
    remaining_daily: Decimal


def get_limits(customer_id: str) -> tuple[CustomerLimits, str]:
    """Rule 1: fall back to defaults when the customer has no custom limits."""
    with store.lock:
        custom = store.limits.get(customer_id)
    if custom is None:
        return DEFAULT_LIMITS, "default"
    return custom, "custom"


def set_limits(customer_id: str, daily_limit: Decimal, per_transfer_limit: Decimal) -> CustomerLimits:
    """Rule 2: both limits > 0 and per_transfer_limit <= daily_limit."""
    if daily_limit <= 0 or per_transfer_limit <= 0:
        raise ValidationError("Limitler sıfırdan büyük olmalıdır")
    if per_transfer_limit > daily_limit:
        raise ValidationError("per_transfer_limit, daily_limit değerini aşamaz")
    limits = CustomerLimits(daily_limit=daily_limit, per_transfer_limit=per_transfer_limit)
    with store.lock:
        # Rule 8: changing limits never touches recorded usage.
        store.limits[customer_id] = limits
    return limits


def authorize(customer_id: str, amount: Decimal, occurred_on: date, description: str | None) -> Decision:
    """Rules 3-7: inclusive limits, per-transfer reason first, only approvals are recorded."""
    if amount <= 0:
        raise ValidationError("amount sıfırdan büyük olmalıdır")
    with store.lock:
        limits, _ = get_limits(customer_id)
        used = store.usage.get((customer_id, occurred_on), Decimal("0"))

        if amount > limits.per_transfer_limit:
            reason = PER_TRANSFER_LIMIT_EXCEEDED
        elif used + amount > limits.daily_limit:
            reason = DAILY_LIMIT_EXCEEDED
        else:
            reason = None

        if reason is None:
            used += amount
            store.usage[(customer_id, occurred_on)] = used
            store.entries.setdefault(customer_id, []).append(Entry(occurred_on, amount, description))

        # Never negative, even if limits were lowered below today's usage.
        remaining = max(limits.daily_limit - used, Decimal("0"))
    return Decision(allowed=reason is None, reason=reason, remaining_daily=remaining)


def statement(customer_id: str, start: date, end: date) -> tuple[list[Entry], Decimal]:
    """Rules 9-10: inclusive range, date-ascending, approval order within a day."""
    if start > end:
        raise ValidationError("from, to tarihinden sonra olamaz")
    with store.lock:
        items = [e for e in store.entries.get(customer_id, []) if start <= e.occurred_on <= end]
    items.sort(key=lambda e: e.occurred_on)  # stable sort keeps approval order
    total = sum((e.amount for e in items), Decimal("0"))
    return items, total
