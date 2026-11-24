"""Transfer business logic."""

import logging
import threading
import uuid
from datetime import datetime, timezone

from . import fees, reports, store
from .errors import AccountAlreadyExists, AccountNotFound, InsufficientFunds, TransferNotFound, ValidationFailed
from .models import AccountCreate, TransferRequest

logger = logging.getLogger("aurora.core")

# Serialises money movement so validate-then-write and idempotency checks are atomic.
_lock = threading.Lock()


def create_account(data: AccountCreate) -> dict:
    with _lock:
        if data.id in store.accounts:
            raise AccountAlreadyExists(data.id)
        account = data.model_dump()
        account["balance"] = fees.to_money(data.balance)
        store.accounts[data.id] = account
    return account


def get_account(account_id: str) -> dict:
    account = store.accounts.get(account_id)
    if account is None:
        raise AccountNotFound(account_id)
    return account


def get_transfer(transfer_id: str) -> dict:
    transfer = store.transfers.get(transfer_id)
    if transfer is None:
        raise TransferNotFound(transfer_id)
    return transfer


def execute_transfer(req: TransferRequest, idempotency_key: str | None = None) -> dict:
    with _lock:
        if idempotency_key and idempotency_key in store.idempotency:
            transfer = store.idempotency[idempotency_key]
            logger.info("Idempotent replay: transfer_id=%s", transfer["id"])
            return transfer

        # Validate everything first; no balance is touched until all checks pass.
        if req.from_account == req.to_account:
            raise ValidationFailed("Gönderen ve alıcı aynı hesap olamaz")
        src = get_account(req.from_account)
        dst = get_account(req.to_account)
        if req.currency != src["currency"] or req.currency != dst["currency"]:
            raise ValidationFailed("Transfer para birimi hesapların para birimiyle eşleşmiyor")

        amount = fees.to_money(req.amount)
        fee = fees.fee_for(amount)
        total = amount + fee
        if src["balance"] < total:
            raise InsufficientFunds()

        transfer = {
            "id": str(uuid.uuid4()),
            "from_account": req.from_account,
            "to_account": req.to_account,
            "amount": amount,
            "fee": fee,
            "currency": req.currency,
            "status": "COMPLETED",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        # The only step that can fail (SQLite) runs before any balance is touched, so a failure
        # leaves every balance and record unchanged (handbook section 2, atomicity).
        reports.record_transfer(transfer, src["owner_name"])

        # Write phase: plain in-memory assignments, cannot fail part-way.
        src["balance"] = src["balance"] - total
        dst["balance"] = dst["balance"] + amount
        store.transfers[transfer["id"]] = transfer
        if idempotency_key:
            store.idempotency[idempotency_key] = transfer

    logger.info(
        "Transfer completed: transfer_id=%s from=%s to=%s",
        transfer["id"],
        req.from_account,
        req.to_account,
    )
    return transfer
