"""Transfer fee calculation. See docs/FEE-POLICY.md."""

from decimal import ROUND_HALF_UP, Decimal

from services.shared.money import CENT, to_money

THRESHOLD = Decimal("1000.00")
STANDARD_RATE = Decimal("0.005")
REDUCED_RATE = Decimal("0.0025")

__all__ = ["CENT", "THRESHOLD", "STANDARD_RATE", "REDUCED_RATE", "to_money", "fee_for"]


def fee_for(amount: Decimal) -> Decimal:
    """Fee per FEE-POLICY: 0.50% below 1000.00, 0.25% at or above (threshold inclusive)."""
    amount = Decimal(str(amount))
    rate = REDUCED_RATE if amount >= THRESHOLD else STANDARD_RATE
    return (amount * rate).quantize(CENT, rounding=ROUND_HALF_UP)
