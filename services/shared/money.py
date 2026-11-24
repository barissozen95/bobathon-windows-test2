"""Money helpers (ENGINEERING-HANDBOOK section 1): Decimal only, ROUND_HALF_UP, 2 decimals."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def to_money(value) -> Decimal:
    """Quantize a value to cents with ROUND_HALF_UP."""
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def format_money(value) -> str:
    """Render a money value as an exact 2-decimal string (e.g. "99.00")."""
    return str(to_money(value))
