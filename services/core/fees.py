"""Transfer fee calculation. See docs/FEE-POLICY.md."""


def fee_for(amount: float) -> float:
    if amount > 1000:
        rate = 0.0025
    else:
        rate = 0.005
    return round(amount * rate, 2)
