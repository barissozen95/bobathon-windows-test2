"""Core domain errors (ENGINEERING-HANDBOOK section 2 error table)."""

from services.shared.errors import AppError, ValidationFailed

__all__ = [
    "AppError",
    "ValidationFailed",
    "AccountNotFound",
    "AccountAlreadyExists",
    "TransferNotFound",
    "InsufficientFunds",
]


class AccountNotFound(AppError):
    status_code = 404
    code = "ACCOUNT_NOT_FOUND"

    def __init__(self, account_id: str):
        super().__init__(f"Hesap bulunamadı: {account_id}")


class AccountAlreadyExists(AppError):
    status_code = 409
    code = "ACCOUNT_ALREADY_EXISTS"

    def __init__(self, account_id: str):
        super().__init__(f"Hesap zaten var: {account_id}")


class TransferNotFound(AppError):
    status_code = 404
    code = "TRANSFER_NOT_FOUND"

    def __init__(self, transfer_id: str):
        super().__init__(f"Transfer bulunamadı: {transfer_id}")


class InsufficientFunds(AppError):
    status_code = 409
    code = "INSUFFICIENT_FUNDS"

    def __init__(self):
        super().__init__("Yetersiz bakiye (tutar + ücret)")
