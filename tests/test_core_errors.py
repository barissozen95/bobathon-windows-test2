"""API tests for the handbook error envelope (ENGINEERING-HANDBOOK section 2)."""

import logging

import pytest
from fastapi.testclient import TestClient

from services.core import store
from services.core.main import app
from tests.helpers import assert_error

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_store():
    store.reset()


# --- happy path -------------------------------------------------------------


def test_successful_request_returns_no_error_envelope():
    # Arrange
    payload = {"id": "ACC-1", "owner_name": "Ayse Demir", "iban": "TR00A", "balance": "1.00"}
    # Act
    resp = client.post("/accounts", json=payload)
    # Assert
    assert resp.status_code == 201
    assert "error" not in resp.json() and "detail" not in resp.json()


# --- negative ---------------------------------------------------------------


def test_unknown_route_returns_not_found_envelope():
    # Act
    resp = client.get("/olmayan-yol")
    # Assert
    assert_error(resp, 404, "NOT_FOUND")


def test_wrong_method_returns_method_not_allowed_envelope():
    # Act
    resp = client.put("/accounts/X", json={})
    # Assert
    assert_error(resp, 405, "METHOD_NOT_ALLOWED")


_INTERNAL_MARKERS = ("Traceback", "input_value", "type=", "errors.pydantic.dev", 'File "')

_VALIDATION_TRIGGERS = [
    pytest.param("post", "/transfers", {"json": {"from_account": "A", "to_account": "B", "amount": "abc"}},
                 id="amount-not-decimal"),
    pytest.param("post", "/transfers", {"json": {"from_account": "A", "to_account": "B", "amount": ["1"]}},
                 id="amount-wrong-type"),
    pytest.param("post", "/transfers", {"json": {"from_account": "A", "to_account": "B"}},
                 id="missing-field"),
    pytest.param("post", "/transfers", {"json": {"from_account": "A", "to_account": "B", "amount": "1.00",
                                                 "currency": "try"}}, id="currency-pattern"),
    pytest.param("post", "/accounts", {"json": {"id": "X", "owner_name": "", "iban": "TR00X",
                                                "balance": "-1.00"}}, id="multiple-errors"),
    pytest.param("post", "/accounts", {"content": b"{not json", "headers": {"Content-Type": "application/json"}},
                 id="malformed-json"),
    pytest.param("post", "/reports/archive", {"json": {"filename": "../etc/passwd"}},
                 id="custom-validator"),
    pytest.param("get", "/reports/transfers", {}, id="missing-query-param"),
]


@pytest.mark.parametrize("method,path,kwargs", _VALIDATION_TRIGGERS)
def test_validation_error_message_has_no_internal_details(method, path, kwargs):
    # Act
    resp = getattr(client, method)(path, **kwargs)
    # Assert
    body = assert_error(resp, 422, "VALIDATION_ERROR")
    message = body["error"]["message"]
    for marker in _INTERNAL_MARKERS:
        assert marker not in message, f"{marker!r} leaked in: {message}"
        assert marker not in resp.text


def test_unexpected_error_returns_internal_error_envelope(tmp_path, monkeypatch, caplog):
    # Arrange: archives/ exists but reports/ does not -> the archiver raises unexpectedly
    monkeypatch.chdir(tmp_path)
    (tmp_path / "archives").mkdir()
    server_error_client = TestClient(app, raise_server_exceptions=False)
    # Act
    with caplog.at_level(logging.ERROR, logger="aurora.core"):
        resp = server_error_client.post("/reports/archive", json={"filename": "statements"})
    # Assert
    body = assert_error(resp, 500, "INTERNAL_ERROR")
    assert body["error"]["message"] == "Beklenmeyen bir hata oluştu"
    assert "Traceback" not in resp.text and "reports" not in resp.text
    assert "Unhandled error" in caplog.text


# --- boundary ---------------------------------------------------------------


def test_error_envelope_contains_only_code_and_message():
    # Act
    resp = client.get("/accounts/ACC-9999")
    # Assert
    body = assert_error(resp, 404, "ACCOUNT_NOT_FOUND")
    assert set(body["error"]) == {"code", "message"}
