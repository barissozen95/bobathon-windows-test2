"""Backwards-compatible import path for the fee rules (see services/core/domain/fees.py)."""

from .domain.fees import CENT, REDUCED_RATE, STANDARD_RATE, THRESHOLD, fee_for, to_money

__all__ = ["CENT", "THRESHOLD", "STANDARD_RATE", "REDUCED_RATE", "to_money", "fee_for"]
