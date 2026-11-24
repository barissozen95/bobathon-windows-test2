"""Core HTTP routes: translate requests into use-case calls."""

from fastapi import APIRouter, Header

from services.core.application import accounts, reports, transfers

from .schemas import AccountCreate, ArchiveRequest, TransferRequest

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/accounts", status_code=201)
def create_account(data: AccountCreate):
    return accounts.create_account(
        account_id=data.id,
        owner_name=data.owner_name,
        iban=data.iban,
        balance=data.balance,
        currency=data.currency,
    )


@router.get("/accounts/{account_id}")
def get_account(account_id: str):
    return accounts.get_account(account_id)


@router.post("/transfers", status_code=201)
def create_transfer(req: TransferRequest, idempotency_key: str | None = Header(default=None)):
    return transfers.execute_transfer(
        from_account=req.from_account,
        to_account=req.to_account,
        amount=req.amount,
        currency=req.currency,
        idempotency_key=idempotency_key,
    )


@router.get("/transfers/{transfer_id}")
def get_transfer(transfer_id: str):
    return transfers.get_transfer(transfer_id)


@router.get("/reports/transfers")
def transfers_by_owner(owner: str):
    return reports.find_transfers_by_owner(owner)


@router.post("/reports/archive")
def archive(req: ArchiveRequest):
    return {"exit_code": reports.archive_statements(req.filename)}
