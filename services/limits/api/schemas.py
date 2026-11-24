"""Request bodies. Money and dates arrive as strings and are parsed in api/parsing.py."""

from pydantic import BaseModel


class LimitsInput(BaseModel):
    daily_limit: str
    per_transfer_limit: str


class AuthorizeInput(BaseModel):
    amount: str
    occurred_on: str
    description: str | None = None
