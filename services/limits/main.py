"""Aurora Limits & Statements HTTP API (docs/API-SPEC-limits.yaml)."""

import logging
import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import service

logger = logging.getLogger(__name__)

app = FastAPI(title="Aurora Limits & Statements", version="1.0.0")

CUSTOMER_ID_RE = re.compile(r"^C[0-9]{6}$")
MONEY_RE = re.compile(r"^[0-9]+(\.[0-9]{1,2})?$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
CENT = Decimal("0.01")


# --- error envelope -------------------------------------------------------

def _error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


@app.exception_handler(service.ValidationError)
async def _on_validation(_: Request, exc: service.ValidationError):
    return _error(422, "VALIDATION_ERROR", str(exc))


@app.exception_handler(RequestValidationError)
async def _on_request_validation(_: Request, exc: RequestValidationError):
    parts = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err.get("loc", ()) if p not in ("body", "query", "path"))
        parts.append(f"{loc}: {err.get('msg')}" if loc else str(err.get("msg")))
    return _error(422, "VALIDATION_ERROR", "; ".join(parts) or "Geçersiz istek")


@app.exception_handler(StarletteHTTPException)
async def _on_http(_: Request, exc: StarletteHTTPException):
    codes = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
    return _error(exc.status_code, codes.get(exc.status_code, "HTTP_ERROR"), str(exc.detail))


@app.exception_handler(Exception)
async def _on_unexpected(_: Request, exc: Exception):
    logger.exception("Unexpected error in limits service")
    return _error(500, "INTERNAL_ERROR", "Beklenmeyen bir hata oluştu")


# --- input parsing ----------------------------------------------------------

def _customer_id(value: str) -> str:
    if not CUSTOMER_ID_RE.match(value):
        raise service.ValidationError("customer_id 'C' + 6 rakam olmalıdır (örn. C004217)")
    return value


def _money(field: str, value: str) -> Decimal:
    if not MONEY_RE.match(value):
        raise service.ValidationError(f"{field} en fazla 2 ondalıklı pozitif bir sayı olmalıdır")
    return Decimal(value)


def _date(field: str, value: str) -> date:
    if not DATE_RE.match(value):
        raise service.ValidationError(f"{field} YYYY-MM-DD biçiminde olmalıdır")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise service.ValidationError(f"{field} geçerli bir tarih değil") from None


def _fmt(amount: Decimal) -> str:
    return str(amount.quantize(CENT, rounding=ROUND_HALF_UP))


# --- schemas ------------------------------------------------------------------

class LimitsInput(BaseModel):
    daily_limit: str
    per_transfer_limit: str


class AuthorizeInput(BaseModel):
    amount: str
    occurred_on: str
    description: str | None = None


def _limits_body(customer_id: str, limits, source: str) -> dict:
    return {
        "customer_id": customer_id,
        "daily_limit": _fmt(limits.daily_limit),
        "per_transfer_limit": _fmt(limits.per_transfer_limit),
        "source": source,
    }


# --- endpoints ------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.put("/limits/{customer_id}")
def put_limits(customer_id: str, body: LimitsInput):
    cid = _customer_id(customer_id)
    limits = service.set_limits(
        cid,
        _money("daily_limit", body.daily_limit),
        _money("per_transfer_limit", body.per_transfer_limit),
    )
    return _limits_body(cid, limits, "custom")


@app.get("/limits/{customer_id}")
def get_limits(customer_id: str):
    cid = _customer_id(customer_id)
    limits, source = service.get_limits(cid)
    return _limits_body(cid, limits, source)


@app.post("/limits/{customer_id}/authorize")
def authorize(customer_id: str, body: AuthorizeInput):
    cid = _customer_id(customer_id)
    decision = service.authorize(
        cid,
        _money("amount", body.amount),
        _date("occurred_on", body.occurred_on),
        body.description,
    )
    return {
        "customer_id": cid,
        "allowed": decision.allowed,
        "reason": decision.reason,
        "remaining_daily": _fmt(decision.remaining_daily),
    }


@app.get("/statements/{customer_id}")
def get_statement(
    customer_id: str,
    from_: str = Query(..., alias="from"),
    to: str = Query(...),
):
    cid = _customer_id(customer_id)
    start, end = _date("from", from_), _date("to", to)
    items, total = service.statement(cid, start, end)
    return {
        "customer_id": cid,
        "from": start.isoformat(),
        "to": end.isoformat(),
        "entries": [
            {"occurred_on": e.occurred_on.isoformat(), "amount": _fmt(e.amount), "description": e.description}
            for e in items
        ],
        "total": _fmt(total),
    }
