"""Transfer fee calculation. See docs/FEE-POLICY.md."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
THRESHOLD = Decimal("1000.00")
STANDARD_RATE = Decimal("0.005")
REDUCED_RATE = Decimal("0.0025")


def to_money(value) -> Decimal:
    """Quantize a value to cents with ROUND_HALF_UP."""
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def fee_for(amount: Decimal) -> Decimal:
    """Fee per FEE-POLICY: 0.50% below 1000.00, 0.25% at or above (threshold inclusive)."""
    amount = Decimal(str(amount))
    rate = REDUCED_RATE if amount >= THRESHOLD else STANDARD_RATE
    return (amount * rate).quantize(CENT, rounding=ROUND_HALF_UP)
