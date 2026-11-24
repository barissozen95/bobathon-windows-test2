"""Shared helpers for the Aurora Core API tests (ENGINEERING-HANDBOOK section 4).

Imported as `from tests.helpers import ...`. Works in both prepend and importlib import
modes because pytest.ini sets `pythonpath = .`, so the repo root is on sys.path and
`tests` resolves as a (namespace) package.
"""

from decimal import Decimal


def D(value) -> Decimal:
    """Compare money exactly: responses may serialise Decimal as a JSON number (2.5)."""
    return Decimal(str(value))


def assert_error(response, status: int, code: str) -> dict:
    """Assert the handbook error envelope: status, code, message, and no bare `detail`."""
    assert response.status_code == status, response.text
    body = response.json()
    assert "detail" not in body
    assert set(body) == {"error"}
    assert body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]
    return body
