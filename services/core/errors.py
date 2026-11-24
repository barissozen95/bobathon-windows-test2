"""Backwards-compatible import path for core errors (see domain/errors.py, shared/errors.py)."""

from services.shared.errors import INTERNAL_MESSAGE, envelope, install_error_handlers as install

from .domain.errors import (
    AccountAlreadyExists,
    AccountNotFound,
    AppError,
    InsufficientFunds,
    TransferNotFound,
    ValidationFailed,
)

__all__ = [
    "INTERNAL_MESSAGE",
    "envelope",
    "install",
    "AppError",
    "ValidationFailed",
    "AccountNotFound",
    "AccountAlreadyExists",
    "TransferNotFound",
    "InsufficientFunds",
]
