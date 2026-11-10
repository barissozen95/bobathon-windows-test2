"""Mutation plugin for the M4 check (loaded with `-p _mutants`, driven by env MUTANT).

It breaks the participant's code on purpose, in memory, then the participant's own
test-suite runs. A good test-suite FAILS (the mutant is "killed"). If the suite
still passes, the tests are not protecting that behavior.
"""

import os
import sys
from decimal import ROUND_DOWN, Decimal

NAME = os.environ.get("MUTANT", "")
REPORT = os.environ.get("MUTANT_REPORT")
applied = {"touched": False}


def _fee_modules():
    import services.core.fees  # noqa: F401
    import services.core.service  # noqa: F401

    return [m for n, m in list(sys.modules.items()) if n.startswith("services.core") and hasattr(m, "fee_for")]


def _patch_fee(make):
    for module in _fee_modules():
        original = module.fee_for
        module.fee_for = make(original)
        applied["touched"] = True


class _SpyDict(dict):
    """Ignores writes: the idempotency store 'forgets' every key."""

    def __setitem__(self, key, value):
        applied["touched"] = True


def pytest_configure(config):
    if NAME == "fee_threshold":
        # amount == 1000.00 wrongly uses the low (0.50%) rate
        _patch_fee(lambda orig: lambda a, *r, **k: Decimal("5.00") if Decimal(str(a)) == Decimal("1000.00") else orig(a, *r, **k))
    elif NAME == "fee_rounding":
        # ROUND_HALF_UP -> ROUND_DOWN (3.00 -> 0.01 instead of 0.02)
        def make(orig):
            def mutated(a, *r, **k):
                amount = Decimal(str(a))
                rate = Decimal("0.0025") if amount >= Decimal("1000.00") else Decimal("0.005")
                return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

            return mutated

        _patch_fee(make)
    elif NAME == "fee_not_charged":
        _patch_fee(lambda orig: lambda a, *r, **k: Decimal("0.00"))
    elif NAME == "idempotency_off":
        from services.core import store

        store.idempotency = _SpyDict()


def pytest_sessionfinish(session, exitstatus):
    if REPORT:
        with open(REPORT, "w") as fh:
            fh.write("applied" if applied["touched"] else "not-applicable")
