"""Base application error and the handbook error envelope (ENGINEERING-HANDBOOK section 2).

Domain layers raise `AppError` subclasses; only the API layer (via `install_error_handlers`)
knows how they become HTTP responses.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

INTERNAL_MESSAGE = "Beklenmeyen bir hata oluştu"

_HTTP_CODES = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
_HIDDEN_LOC_PARTS = ("body", "query", "path")


class AppError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationFailed(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"


def envelope(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message}})


def _validation_message(exc: RequestValidationError) -> str:
    parts = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err.get("loc", ()) if p not in _HIDDEN_LOC_PARTS)
        msg = err.get("msg", "geçersiz değer")
        parts.append(f"{loc}: {msg}" if loc else msg)
    return "Geçersiz girdi - " + "; ".join(parts) if parts else "Geçersiz girdi"


def install_error_handlers(app: FastAPI, logger: logging.Logger) -> None:
    """Route every error through the single envelope; never leak internals to the client."""

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
        return envelope(exc.status_code, _HTTP_CODES.get(exc.status_code, "HTTP_ERROR"), str(exc.detail))

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return envelope(500, "INTERNAL_ERROR", INTERNAL_MESSAGE)
