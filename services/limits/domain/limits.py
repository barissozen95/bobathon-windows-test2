"""Limit entities and decision rules (PRD section 4). Pure functions, no storage."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from services.shared.errors import ValidationFailed

PER_TRANSFER_LIMIT_EXCEEDED = "PER_TRANSFER_LIMIT_EXCEEDED"
DAILY_LIMIT_EXCEEDED = "DAILY_LIMIT_EXCEEDED"


@dataclass(frozen=True)
class CustomerLimits:
    daily_limit: Decimal
    per_transfer_limit: Decimal


@dataclass(frozen=True)
class Entry:
    occurred_on: date
    amount: Decimal
    description: str | None


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str | None
    remaining_daily: Decimal


DEFAULT_LIMITS = CustomerLimits(daily_limit=Decimal("10000.00"), per_transfer_limit=Decimal("5000.00"))


def new_limits(daily_limit: Decimal, per_transfer_limit: Decimal) -> CustomerLimits:
    """Rule 2: both limits > 0 and per_transfer_limit <= daily_limit."""
    if daily_limit <= 0 or per_transfer_limit <= 0:
        raise ValidationFailed("Limitler sıfırdan büyük olmalıdır")
    if per_transfer_limit > daily_limit:
        raise ValidationFailed("per_transfer_limit, daily_limit değerini aşamaz")
    return CustomerLimits(daily_limit=daily_limit, per_transfer_limit=per_transfer_limit)


def rejection_reason(limits: CustomerLimits, used_today: Decimal, amount: Decimal) -> str | None:
    """Rules 3-5: inclusive limits, per-transfer reason takes precedence."""
    if amount <= 0:
        raise ValidationFailed("amount sıfırdan büyük olmalıdır")
    if amount > limits.per_transfer_limit:
        return PER_TRANSFER_LIMIT_EXCEEDED
    if used_today + amount > limits.daily_limit:
        return DAILY_LIMIT_EXCEEDED
    return None


def remaining_daily(limits: CustomerLimits, used_today: Decimal) -> Decimal:
    """Never negative, even if limits were lowered below today's usage."""
    return max(limits.daily_limit - used_today, Decimal("0"))
