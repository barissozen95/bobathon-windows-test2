"""Aurora Core entry point (`uvicorn services.core.main:app`). See services/core/api/app.py."""

from .api.app import app, create_app

__all__ = ["app", "create_app"]
