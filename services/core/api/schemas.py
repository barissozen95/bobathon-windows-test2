import re
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

# Money is always Decimal with at most 2 decimal places (ENGINEERING-HANDBOOK section 1).
# Currency is an ISO 4217-style code: exactly three upper-case letters (e.g. TRY, USD).
CURRENCY_PATTERN = r"^[A-Z]{3}$"


class AccountCreate(BaseModel):
    id: str = Field(min_length=1)
    owner_name: str = Field(min_length=1)
    iban: str = Field(min_length=1)
    balance: Decimal = Field(ge=0, decimal_places=2, allow_inf_nan=False)
    currency: str = Field(default="TRY", pattern=CURRENCY_PATTERN)


class TransferRequest(BaseModel):
    from_account: str = Field(min_length=1)
    to_account: str = Field(min_length=1)
    amount: Decimal = Field(gt=0, decimal_places=2, allow_inf_nan=False)
    currency: str = Field(default="TRY", pattern=CURRENCY_PATTERN)
    note: str | None = None


_SAFE_FILENAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}")


class ArchiveRequest(BaseModel):
    filename: str

    @field_validator("filename")
    @classmethod
    def _safe_filename(cls, value: str) -> str:
        # Handbook section 5: file names are validated, no path traversal, no shell metacharacters.
        if not _SAFE_FILENAME.fullmatch(value) or ".." in value:
            raise ValueError("dosya adı yalnızca harf, rakam, '.', '_' ve '-' içerebilir; '..' yasak")
        return value
