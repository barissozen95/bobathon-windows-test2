"""Strict parsing of path/body values into domain types (raises VALIDATION_ERROR)."""

import re
from datetime import date
from decimal import Decimal

from services.shared.errors import ValidationFailed

CUSTOMER_ID_RE = re.compile(r"^C[0-9]{6}$")
MONEY_RE = re.compile(r"^[0-9]+(\.[0-9]{1,2})?$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


def customer_id(value: str) -> str:
    if not CUSTOMER_ID_RE.match(value):
        raise ValidationFailed("customer_id 'C' + 6 rakam olmalıdır (örn. C004217)")
    return value


def money(field: str, value: str) -> Decimal:
    if not MONEY_RE.match(value):
        raise ValidationFailed(f"{field} en fazla 2 ondalıklı pozitif bir sayı olmalıdır")
    return Decimal(value)


def iso_date(field: str, value: str) -> date:
    if not DATE_RE.match(value):
        raise ValidationFailed(f"{field} YYYY-MM-DD biçiminde olmalıdır")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValidationFailed(f"{field} geçerli bir tarih değil") from None
