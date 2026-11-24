"""API tests for Aurora Core transfers: POST /transfers and GET /transfers/{id}."""

import logging

import pytest
from fastapi.testclient import TestClient

from services.core import store
from services.core.main import app
from tests.helpers import D, assert_error

client = TestClient(app)

OWNER_A, IBAN_A = "Ayse Demir", "TR544675118651433004071029"
OWNER_B, IBAN_B = "Mehmet Arslan", "TR142771657106125823036929"


@pytest.fixture(autouse=True)
def _reset_store():
    store.reset()


def _account(account_id, balance, owner="Test Kisi", iban=None, currency="TRY"):
    resp = client.post(
        "/accounts",
        json={"id": account_id, "owner_name": owner, "iban": iban or f"TR00{account_id}",
              "balance": balance, "currency": currency},
    )
    assert resp.status_code == 201, resp.text
    return resp


def _transfer(amount, src="A", dst="B", key=None, **extra):
    headers = {"Idempotency-Key": key} if key else {}
    return client.post("/transfers", json={"from_account": src, "to_account": dst, "amount": amount, **extra},
                       headers=headers)


def _balance(account_id):
    return D(client.get(f"/accounts/{account_id}").json()["balance"])


def _setup_pair(a="1000.00", b="0.00"):
    _account("A", a, owner=OWNER_A, iban=IBAN_A)
    _account("B", b, owner=OWNER_B, iban=IBAN_B)


# --- happy path -------------------------------------------------------------


def test_transfer_moves_amount_and_charges_fee():
    # Arrange
    _setup_pair()
    # Act
    resp = _transfer("100.00")
    # Assert
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "COMPLETED"
    assert D(body["amount"]) == D("100.00")
    assert D(body["fee"]) == D("0.50")
    assert _balance("A") == D("899.50")
    assert _balance("B") == D("100.00")


@pytest.mark.parametrize("currency", ["TRY", "USD"])
def test_transfer_accepts_valid_currency(currency):
    # Arrange
    _account("A", "1000.00", currency=currency)
    _account("B", "0.00", currency=currency)
    # Act
    resp = _transfer("100.00", currency=currency)
    # Assert
    assert resp.status_code == 201
    assert resp.json()["currency"] == currency
    assert _balance("A") == D("899.50")
    assert _balance("B") == D("100.00")


def test_get_transfer_returns_created_transfer():
    # Arrange
    _setup_pair()
    created = _transfer("10.00").json()
    # Act
    resp = client.get(f"/transfers/{created['id']}")
    # Assert
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]
    assert D(resp.json()["amount"]) == D("10.00")


def test_transfer_idempotent_replay_returns_first_response():
    # Arrange
    _setup_pair()
    first = _transfer("100.00", key="key-1")
    # Act
    second = _transfer("100.00", key="key-1")
    # Assert
    assert first.status_code == 201 and second.status_code == 201
    assert second.json() == first.json()
    assert _balance("A") == D("899.50")
    assert _balance("B") == D("100.00")


def test_transfer_idempotent_replay_ignores_different_body():
    # Arrange
    _setup_pair()
    first = _transfer("100.00", key="key-1").json()
    # Act
    second = _transfer("200.00", key="key-1").json()
    # Assert
    assert second["id"] == first["id"]
    assert D(second["amount"]) == D("100.00")
    assert _balance("A") == D("899.50")
    assert _balance("B") == D("100.00")


def test_transfer_without_idempotency_key_creates_new_transfer_each_time():
    # Arrange
    _setup_pair()
    # Act
    first = _transfer("100.00").json()
    second = _transfer("100.00").json()
    # Assert
    assert first["id"] != second["id"]
    assert _balance("A") == D("799.00")


def test_transfer_retry_after_failed_key_creates_transfer():
    # Arrange
    _setup_pair(a="50.00")
    failed = _transfer("100.00", key="key-retry")
    _account("C", "1000.00")
    # Act
    retried = _transfer("100.00", src="C", key="key-retry")
    # Assert
    assert_error(failed, 409, "INSUFFICIENT_FUNDS")
    assert retried.status_code == 201
    assert retried.json()["from_account"] == "C"
    assert _balance("C") == D("899.50")


def test_transfer_logs_contain_no_pii(caplog):
    # Arrange
    _setup_pair()
    # Act
    with caplog.at_level(logging.DEBUG):
        resp = _transfer("100.00")
        _transfer("100.00", src="A", dst="A")
        _transfer("999999.00")
    # Assert
    assert resp.status_code == 201
    for secret in (OWNER_A, OWNER_B, IBAN_A, IBAN_B):
        assert secret not in caplog.text
    assert resp.json()["id"] in caplog.text


# --- negative ---------------------------------------------------------------


@pytest.mark.parametrize("amount", ["0.00", "-0.01", "NaN", "Infinity", "abc"])
def test_transfer_rejects_invalid_amount(amount):
    # Arrange
    _setup_pair()
    # Act
    resp = _transfer(amount)
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert _balance("A") == D("1000.00")
    assert _balance("B") == D("0.00")


@pytest.mark.parametrize("missing", ["from_account", "to_account", "amount"])
def test_transfer_rejects_missing_field(missing):
    # Arrange
    _setup_pair()
    body = {"from_account": "A", "to_account": "B", "amount": "10.00"}
    del body[missing]
    # Act
    resp = client.post("/transfers", json=body)
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert _balance("A") == D("1000.00")


def test_transfer_rejects_same_sender_and_receiver():
    # Arrange
    _setup_pair()
    # Act
    resp = _transfer("100.00", src="A", dst="A")
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert _balance("A") == D("1000.00")
    assert client.get("/reports/transfers", params={"owner": OWNER_A}).json() == []


@pytest.mark.parametrize("src,dst", [("", "B"), ("A", "")])
def test_transfer_rejects_empty_account_id(src, dst):
    # Arrange
    _setup_pair()
    # Act
    resp = _transfer("10.00", src=src, dst=dst)
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert _balance("A") == D("1000.00")


def test_transfer_returns_404_when_sender_unknown():
    # Arrange
    _account("B", "100.00")
    # Act
    resp = _transfer("10.00", src="ACC-9999", dst="B")
    # Assert
    assert_error(resp, 404, "ACCOUNT_NOT_FOUND")
    assert _balance("B") == D("100.00")


def test_transfer_returns_404_when_receiver_unknown():
    # Arrange
    _account("A", "100.00")
    # Act
    resp = _transfer("10.00", src="A", dst="ACC-9999")
    # Assert
    assert_error(resp, 404, "ACCOUNT_NOT_FOUND")
    assert _balance("A") == D("100.00")


def test_transfer_rejects_currency_mismatch():
    # Arrange
    _setup_pair()
    # Act
    resp = _transfer("10.00", currency="USD")
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert _balance("A") == D("1000.00")
    assert _balance("B") == D("0.00")


def test_transfer_rejects_accounts_with_different_currencies():
    # Arrange
    _account("A", "1000.00")
    _account("B", "0.00", currency="EUR")
    # Act
    resp = _transfer("10.00")
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert _balance("A") == D("1000.00")
    assert _balance("B") == D("0.00")


@pytest.mark.parametrize("currency", ["", "TR", "TRYY", "try", "T1Y"])
def test_transfer_rejects_invalid_currency(currency):
    # Arrange
    _setup_pair()
    # Act
    resp = _transfer("10.00", currency=currency)
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert _balance("A") == D("1000.00")
    assert _balance("B") == D("0.00")


def test_get_transfer_returns_404_when_unknown():
    # Act
    resp = client.get("/transfers/TRF-9999")
    # Assert
    body = assert_error(resp, 404, "TRANSFER_NOT_FOUND")
    assert "TRF-9999" in body["error"]["message"]


# --- boundary ---------------------------------------------------------------


def test_transfer_accepts_minimum_amount_with_zero_fee():
    # Arrange
    _setup_pair()
    # Act
    resp = _transfer("0.01")
    # Assert
    assert resp.status_code == 201
    assert D(resp.json()["fee"]) == D("0.00")
    assert _balance("A") == D("999.99")
    assert _balance("B") == D("0.01")


@pytest.mark.parametrize("currency,status", [("TR", 422), ("TRY", 201), ("TRYY", 422)])
def test_transfer_currency_length_boundary(currency, status):
    # Arrange
    _setup_pair()
    # Act
    resp = _transfer("100.00", currency=currency)
    # Assert
    if status == 201:
        assert resp.status_code == 201
        assert _balance("A") == D("899.50")
    else:
        assert_error(resp, 422, "VALIDATION_ERROR")
        assert _balance("A") == D("1000.00")


@pytest.mark.parametrize("amount", ["0.009", "10.001"])
def test_transfer_rejects_amount_with_three_decimals(amount):
    # Arrange
    _setup_pair()
    # Act
    resp = _transfer(amount)
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert _balance("A") == D("1000.00")


def test_transfer_rejects_balance_one_cent_below_amount_plus_fee():
    # Arrange: 100.00 + fee 0.50 = 100.50 needed
    _setup_pair(a="100.49")
    # Act
    resp = _transfer("100.00", key="k-insufficient")
    # Assert
    assert_error(resp, 409, "INSUFFICIENT_FUNDS")
    assert _balance("A") == D("100.49")
    assert _balance("B") == D("0.00")
    assert client.get("/reports/transfers", params={"owner": OWNER_A}).json() == []


def test_transfer_rejects_balance_equal_to_amount_without_fee():
    # Arrange
    _setup_pair(a="100.00")
    # Act
    resp = _transfer("100.00")
    # Assert
    assert_error(resp, 409, "INSUFFICIENT_FUNDS")
    assert _balance("A") == D("100.00")
    assert _balance("B") == D("0.00")


def test_transfer_accepts_balance_exactly_amount_plus_fee():
    # Arrange
    _setup_pair(a="100.50")
    # Act
    resp = _transfer("100.00")
    # Assert
    assert resp.status_code == 201
    assert _balance("A") == D("0.00")
    assert _balance("B") == D("100.00")
