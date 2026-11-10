"""Aurora Core: account and transfer API."""

from fastapi import FastAPI, Header, HTTPException

from . import reports, service, store
from .models import AccountCreate, ArchiveRequest, TransferRequest

app = FastAPI(title="Aurora Core", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/accounts", status_code=201)
def create_account(data: AccountCreate):
    return service.create_account(data)


@app.get("/accounts/{account_id}")
def get_account(account_id: str):
    account = store.accounts.get(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.post("/transfers", status_code=201)
def create_transfer(req: TransferRequest, idempotency_key: str | None = Header(default=None)):
    return service.execute_transfer(req, idempotency_key)


@app.get("/transfers/{transfer_id}")
def get_transfer(transfer_id: str):
    transfer = store.transfers.get(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


@app.get("/reports/transfers")
def transfers_by_owner(owner: str):
    return reports.find_transfers_by_owner(owner)


@app.post("/reports/archive")
def archive(req: ArchiveRequest):
    return {"exit_code": reports.archive_statements(req.filename)}
