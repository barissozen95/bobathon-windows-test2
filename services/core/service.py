"""Transfer business logic."""

import logging
import uuid
from datetime import datetime, timezone

from . import fees, reports, store
from .models import AccountCreate, TransferRequest

logger = logging.getLogger("aurora.core")


def create_account(data: AccountCreate) -> dict:
    account = data.model_dump()
    store.accounts[data.id] = account
    return account


def execute_transfer(req: TransferRequest, idempotency_key: str | None = None) -> dict:
    src = store.accounts[req.from_account]
    fee = fees.fee_for(req.amount)
    total = req.amount + fee

    if src["balance"] < total:
        raise Exception("insufficient funds")

    src["balance"] = src["balance"] - total
    logger.info(
        "Transfer started: %s (%s) new balance=%s",
        src["owner_name"],
        src["iban"],
        src["balance"],
    )

    dst = store.accounts[req.to_account]
    dst["balance"] = dst["balance"] + req.amount

    transfer = {
        "id": str(uuid.uuid4()),
        "from_account": req.from_account,
        "to_account": req.to_account,
        "amount": req.amount,
        "fee": fee,
        "currency": req.currency,
        "status": "COMPLETED",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    store.transfers[transfer["id"]] = transfer
    reports.record_transfer(transfer, src["owner_name"])

    logger.info(
        "Transfer completed: %s -> %s (%s)",
        src["owner_name"],
        dst["owner_name"],
        dst["iban"],
    )
    return transfer
