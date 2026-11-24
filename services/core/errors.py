"""Domain errors and the handbook error envelope (ENGINEERING-HANDBOOK section 2)."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("aurora.core")

INTERNAL_MESSAGE = "Beklenmeyen bir hata oluştu"


class AppError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationFailed(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"


class AccountNotFound(AppError):
    status_code = 404
    code = "ACCOUNT_NOT_FOUND"

    def __init__(self, account_id: str):
        super().__init__(f"Hesap bulunamadı: {account_id}")


class AccountAlreadyExists(AppError):
    status_code = 409
    code = "ACCOUNT_ALREADY_EXISTS"

    def __init__(self, account_id: str):
        super().__init__(f"Hesap zaten var: {account_id}")


class TransferNotFound(AppError):
    status_code = 404
    code = "TRANSFER_NOT_FOUND"

    def __init__(self, transfer_id: str):
        super().__init__(f"Transfer bulunamadı: {transfer_id}")


class InsufficientFunds(AppError):
    status_code = 409
    code = "INSUFFICIENT_FUNDS"

    def __init__(self):
        super().__init__("Yetersiz bakiye (tutar + ücret)")


def envelope(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message}})


def _validation_message(exc: RequestValidationError) -> str:
    parts = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err.get("loc", ()) if p != "body")
        parts.append(f"{loc}: {err.get('msg', 'geçersiz değer')}" if loc else err.get("msg", "geçersiz değer"))
    return "Geçersiz girdi - " + "; ".join(parts) if parts else "Geçersiz girdi"


_HTTP_CODES = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}


def install(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError):
        return envelope(exc.status_code, exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError):
        return envelope(422, "VALIDATION_ERROR", _validation_message(exc))

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException):
        if exc.status_code >= 500:
            return envelope(500, "INTERNAL_ERROR", INTERNAL_MESSAGE)
        code = _HTTP_CODES.get(exc.status_code, "HTTP_ERROR")
        return envelope(exc.status_code, code, str(exc.detail))

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return envelope(500, "INTERNAL_ERROR", INTERNAL_MESSAGE)
