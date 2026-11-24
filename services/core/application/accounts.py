"""Account use cases."""

from decimal import Decimal

from services.core.domain import fees
from services.core.domain.errors import AccountAlreadyExists, AccountNotFound
from services.core.infrastructure import memory_store


def create_account(*, account_id: str, owner_name: str, iban: str, balance: Decimal, currency: str) -> dict:
    with memory_store.lock:
        if account_id in memory_store.accounts:
            raise AccountAlreadyExists(account_id)
        account = {
            "id": account_id,
            "owner_name": owner_name,
            "iban": iban,
            "balance": fees.to_money(balance),
            "currency": currency,
        }
        memory_store.accounts[account_id] = account
    return account


def get_account(account_id: str) -> dict:
    account = memory_store.accounts.get(account_id)
    if account is None:
        raise AccountNotFound(account_id)
    return account
