"""Limits & Statements HTTP routes."""

from fastapi import APIRouter, Query

from services.limits.application import limits as limits_uc
from services.limits.application import statements as statements_uc
from services.limits.domain.limits import CustomerLimits
from services.shared.money import format_money

from . import parsing
from .schemas import AuthorizeInput, LimitsInput

router = APIRouter()


def _limits_body(cid: str, limits: CustomerLimits, source: str) -> dict:
    return {
        "customer_id": cid,
        "daily_limit": format_money(limits.daily_limit),
        "per_transfer_limit": format_money(limits.per_transfer_limit),
        "source": source,
    }


@router.get("/health")
def health():
    return {"status": "ok"}


@router.put("/limits/{customer_id}")
def put_limits(customer_id: str, body: LimitsInput):
    cid = parsing.customer_id(customer_id)
    limits = limits_uc.set_limits(
        cid,
        parsing.money("daily_limit", body.daily_limit),
        parsing.money("per_transfer_limit", body.per_transfer_limit),
    )
    return _limits_body(cid, limits, "custom")


@router.get("/limits/{customer_id}")
def get_limits(customer_id: str):
    cid = parsing.customer_id(customer_id)
    limits, source = limits_uc.get_limits(cid)
    return _limits_body(cid, limits, source)


@router.post("/limits/{customer_id}/authorize")
def authorize(customer_id: str, body: AuthorizeInput):
    cid = parsing.customer_id(customer_id)
    decision = limits_uc.authorize(
        cid,
        parsing.money("amount", body.amount),
        parsing.iso_date("occurred_on", body.occurred_on),
        body.description,
    )
    return {
        "customer_id": cid,
        "allowed": decision.allowed,
        "reason": decision.reason,
        "remaining_daily": format_money(decision.remaining_daily),
    }


@router.get("/statements/{customer_id}")
def get_statement(customer_id: str, from_: str = Query(..., alias="from"), to: str = Query(...)):
    cid = parsing.customer_id(customer_id)
    start, end = parsing.iso_date("from", from_), parsing.iso_date("to", to)
    items, total = statements_uc.statement(cid, start, end)
    return {
        "customer_id": cid,
        "from": start.isoformat(),
        "to": end.isoformat(),
        "entries": [
            {"occurred_on": e.occurred_on.isoformat(), "amount": format_money(e.amount), "description": e.description}
            for e in items
        ],
        "total": format_money(total),
    }
