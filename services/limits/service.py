"""Backwards-compatible import path for limits use cases (see services/limits/application/)."""

from services.shared.errors import ValidationFailed as ValidationError

from .application.limits import authorize, get_limits, set_limits
from .application.statements import statement
from .domain.limits import (
    DAILY_LIMIT_EXCEEDED,
    DEFAULT_LIMITS,
    PER_TRANSFER_LIMIT_EXCEEDED,
    Decision,
)

__all__ = [
    "ValidationError",
    "authorize",
    "get_limits",
    "set_limits",
    "statement",
    "DAILY_LIMIT_EXCEEDED",
    "DEFAULT_LIMITS",
    "PER_TRANSFER_LIMIT_EXCEEDED",
    "Decision",
]
