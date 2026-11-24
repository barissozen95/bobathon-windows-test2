"""API tests for Aurora Core accounts: POST /accounts and GET /accounts/{id}."""

import pytest
from fastapi.testclient import TestClient

from services.core import store
from services.core.main import app
from tests.helpers import D, assert_error

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_store():
    store.reset()


def _payload(**overrides):
    body = {"id": "ACC-1", "owner_name": "Ayse Demir", "iban": "TR000000000000000000000001", "balance": "500.00"}
    body.update(overrides)
    return body


# --- happy path -------------------------------------------------------------


def test_create_account_returns_201_with_account():
    # Act
    resp = client.post("/accounts", json=_payload())
    # Assert
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == "ACC-1"
    assert body["currency"] == "TRY"
    assert D(body["balance"]) == D("500.00")


def test_get_account_returns_created_account():
    # Arrange
    client.post("/accounts", json=_payload(balance="123.45"))
    # Act
    resp = client.get("/accounts/ACC-1")
    # Assert
    assert resp.status_code == 200
    assert resp.json()["id"] == "ACC-1"
    assert D(resp.json()["balance"]) == D("123.45")


# --- negative ---------------------------------------------------------------


def test_create_account_rejects_duplicate_id():
    # Arrange
    client.post("/accounts", json=_payload(balance="500.00"))
    # Act
    resp = client.post("/accounts", json=_payload(balance="1.00"))
    # Assert
    assert_error(resp, 409, "ACCOUNT_ALREADY_EXISTS")
    assert D(client.get("/accounts/ACC-1").json()["balance"]) == D("500.00")


def test_create_account_rejects_negative_balance():
    # Act
    resp = client.post("/accounts", json=_payload(balance="-0.01"))
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert_error(client.get("/accounts/ACC-1"), 404, "ACCOUNT_NOT_FOUND")


@pytest.mark.parametrize("balance", ["NaN", "Infinity", "-Infinity", "abc"])
def test_create_account_rejects_non_numeric_balance(balance):
    # Act
    resp = client.post("/accounts", json=_payload(balance=balance))
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")


def test_create_account_rejects_empty_id():
    # Act
    resp = client.post("/accounts", json=_payload(id=""))
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")


@pytest.mark.parametrize("field", ["owner_name", "iban"])
def test_create_account_rejects_empty_required_string(field):
    # Act
    resp = client.post("/accounts", json=_payload(**{field: ""}))
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert_error(client.get("/accounts/ACC-1"), 404, "ACCOUNT_NOT_FOUND")


@pytest.mark.parametrize("currency", ["", "TR", "TRYY", "try", "T1Y"])
def test_create_account_rejects_invalid_currency(currency):
    # Act
    resp = client.post("/accounts", json=_payload(currency=currency))
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert_error(client.get("/accounts/ACC-1"), 404, "ACCOUNT_NOT_FOUND")


@pytest.mark.parametrize("missing", ["id", "owner_name", "iban", "balance"])
def test_create_account_rejects_missing_field(missing):
    # Arrange
    body = _payload()
    del body[missing]
    # Act
    resp = client.post("/accounts", json=body)
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")


def test_create_account_rejects_missing_body():
    # Act
    resp = client.post("/accounts")
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")


def test_create_account_rejects_malformed_json():
    # Act
    resp = client.post("/accounts", content=b"{not json", headers={"Content-Type": "application/json"})
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")


def test_get_account_returns_404_when_unknown():
    # Act
    resp = client.get("/accounts/ACC-9999")
    # Assert
    body = assert_error(resp, 404, "ACCOUNT_NOT_FOUND")
    assert body["error"]["message"] == "Hesap bulunamadı: ACC-9999"


# --- boundary ---------------------------------------------------------------


def test_create_account_accepts_zero_balance():
    # Act
    resp = client.post("/accounts", json=_payload(balance="0.00"))
    # Assert
    assert resp.status_code == 201
    assert D(resp.json()["balance"]) == D("0.00")


def test_create_account_rejects_balance_with_three_decimals():
    # Act
    resp = client.post("/accounts", json=_payload(balance="10.001"))
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")


@pytest.mark.parametrize("field", ["owner_name", "iban"])
def test_create_account_accepts_single_char_required_string(field):
    # Act
    resp = client.post("/accounts", json=_payload(**{field: "X"}))
    # Assert
    assert resp.status_code == 201
    assert client.get("/accounts/ACC-1").json()[field] == "X"


@pytest.mark.parametrize("currency", ["TRY", "USD"])
def test_create_account_accepts_valid_currency(currency):
    # Act
    resp = client.post("/accounts", json=_payload(currency=currency))
    # Assert
    assert resp.status_code == 201
    assert resp.json()["currency"] == currency


@pytest.mark.parametrize("currency,status", [("TR", 422), ("TRY", 201), ("TRYY", 422)])
def test_create_account_currency_length_boundary(currency, status):
    # Act
    resp = client.post("/accounts", json=_payload(currency=currency))
    # Assert
    if status == 201:
        assert resp.status_code == 201
        assert resp.json()["currency"] == currency
    else:
        assert_error(resp, 422, "VALIDATION_ERROR")


def test_create_account_accepts_balance_with_two_decimals():
    # Act
    resp = client.post("/accounts", json=_payload(balance="10.01"))
    # Assert
    assert resp.status_code == 201
    assert D(resp.json()["balance"]) == D("10.01")
