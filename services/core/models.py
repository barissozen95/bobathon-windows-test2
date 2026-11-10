from pydantic import BaseModel


class AccountCreate(BaseModel):
    id: str
    owner_name: str
    iban: str
    balance: float
    currency: str = "TRY"


class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: float
    currency: str = "TRY"
    note: str | None = None


class ArchiveRequest(BaseModel):
    filename: str
