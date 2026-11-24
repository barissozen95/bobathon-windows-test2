"""Backwards-compatible import path for request schemas (see services/core/api/schemas.py)."""

from .api.schemas import AccountCreate, ArchiveRequest, TransferRequest

__all__ = ["AccountCreate", "ArchiveRequest", "TransferRequest"]
