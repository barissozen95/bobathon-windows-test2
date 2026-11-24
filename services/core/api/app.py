"""Aurora Core composition root: builds the FastAPI app."""

import logging

from fastapi import FastAPI

from services.shared.errors import install_error_handlers

from .routes import router

logger = logging.getLogger("aurora.core")


def create_app() -> FastAPI:
    app = FastAPI(title="Aurora Core", version="0.1.0")
    install_error_handlers(app, logger)
    app.include_router(router)
    return app


app = create_app()
