"""Limit management and authorization use cases."""

from datetime import date
from decimal import Decimal

from services.limits.domain import limits as rules
from services.limits.domain.limits import CustomerLimits, Decision, Entry
from services.limits.infrastructure import memory_store


def get_limits(customer_id: str) -> tuple[CustomerLimits, str]:
    """Rule 1: fall back to defaults when the customer has no custom limits."""
    with memory_store.lock:
        custom = memory_store.limits.get(customer_id)
    if custom is None:
        return rules.DEFAULT_LIMITS, "default"
    return custom, "custom"


def set_limits(customer_id: str, daily_limit: Decimal, per_transfer_limit: Decimal) -> CustomerLimits:
    new = rules.new_limits(daily_limit, per_transfer_limit)
    with memory_store.lock:
        # Rule 8: changing limits never touches recorded usage.
        memory_store.limits[customer_id] = new
    return new


def authorize(customer_id: str, amount: Decimal, occurred_on: date, description: str | None) -> Decision:
    """Rules 3-7: only approvals are recorded."""
    with memory_store.lock:
        current, _ = get_limits(customer_id)
        used = memory_store.usage.get((customer_id, occurred_on), Decimal("0"))
        reason = rules.rejection_reason(current, used, amount)
        if reason is None:
            used += amount
            memory_store.usage[(customer_id, occurred_on)] = used
            memory_store.entries.setdefault(customer_id, []).append(Entry(occurred_on, amount, description))
        remaining = rules.remaining_daily(current, used)
    return Decision(allowed=reason is None, reason=reason, remaining_daily=remaining)
