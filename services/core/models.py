from decimal import Decimal

from pydantic import BaseModel, Field

# Money is always Decimal with at most 2 decimal places (ENGINEERING-HANDBOOK section 1).


class AccountCreate(BaseModel):
    id: str = Field(min_length=1)
    owner_name: str
    iban: str
    balance: Decimal = Field(ge=0, decimal_places=2, allow_inf_nan=False)
    currency: str = "TRY"


class TransferRequest(BaseModel):
    from_account: str = Field(min_length=1)
    to_account: str = Field(min_length=1)
    amount: Decimal = Field(gt=0, decimal_places=2, allow_inf_nan=False)
    currency: str = "TRY"
    note: str | None = None


class ArchiveRequest(BaseModel):
    filename: str
