"""Aurora Limits & Statements composition root."""

import logging

from fastapi import FastAPI

from services.shared.errors import install_error_handlers

from .routes import router

logger = logging.getLogger("aurora.limits")


def create_app() -> FastAPI:
    app = FastAPI(title="Aurora Limits & Statements", version="1.0.0")
    install_error_handlers(app, logger)
    app.include_router(router)
    return app


app = create_app()
