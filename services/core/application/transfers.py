"""Transfer use cases: atomic, idempotent money movement (handbook section 2)."""

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from services.core.domain import fees
from services.core.domain.errors import InsufficientFunds, TransferNotFound, ValidationFailed
from services.core.infrastructure import memory_store, transfer_log

from .accounts import get_account

logger = logging.getLogger("aurora.core")


def get_transfer(transfer_id: str) -> dict:
    transfer = memory_store.transfers.get(transfer_id)
    if transfer is None:
        raise TransferNotFound(transfer_id)
    return transfer


def execute_transfer(
    *,
    from_account: str,
    to_account: str,
    amount: Decimal,
    currency: str,
    idempotency_key: str | None = None,
) -> dict:
    with memory_store.lock:
        if idempotency_key and idempotency_key in memory_store.idempotency:
            transfer = memory_store.idempotency[idempotency_key]
            logger.info("Idempotent replay: transfer_id=%s", transfer["id"])
            return transfer

        # Validate everything first; no balance is touched until all checks pass.
        if from_account == to_account:
            raise ValidationFailed("Gönderen ve alıcı aynı hesap olamaz")
        src = get_account(from_account)
        dst = get_account(to_account)
        if currency != src["currency"] or currency != dst["currency"]:
            raise ValidationFailed("Transfer para birimi hesapların para birimiyle eşleşmiyor")

        amount = fees.to_money(amount)
        fee = fees.fee_for(amount)
        total = amount + fee
        if src["balance"] < total:
            raise InsufficientFunds()

        transfer = {
            "id": str(uuid.uuid4()),
            "from_account": from_account,
            "to_account": to_account,
            "amount": amount,
            "fee": fee,
            "currency": currency,
            "status": "COMPLETED",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        # The only step that can fail (SQLite) runs before any balance is touched, so a failure
        # leaves every balance and record unchanged (handbook section 2, atomicity).
        transfer_log.record(transfer, src["owner_name"])

        # Write phase: plain in-memory assignments, cannot fail part-way.
        src["balance"] = src["balance"] - total
        dst["balance"] = dst["balance"] + amount
        memory_store.transfers[transfer["id"]] = transfer
        if idempotency_key:
            memory_store.idempotency[idempotency_key] = transfer

    logger.info("Transfer completed: transfer_id=%s from=%s to=%s", transfer["id"], from_account, to_account)
    return transfer
