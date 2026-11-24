"""API tests for the transfer fee (docs/FEE-POLICY.md), observed via POST /transfers."""

import pytest
from fastapi.testclient import TestClient

from services.core import store
from services.core.main import app
from tests.helpers import D, assert_error

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_store():
    store.reset()


def _setup_pair(a="100000.00", b="0.00"):
    for account_id, balance in (("A", a), ("B", b)):
        resp = client.post("/accounts", json={"id": account_id, "owner_name": "Test Kisi",
                                              "iban": f"TR00{account_id}", "balance": balance})
        assert resp.status_code == 201


def _transfer(amount):
    return client.post("/transfers", json={"from_account": "A", "to_account": "B", "amount": amount})


def _balance(account_id):
    return D(client.get(f"/accounts/{account_id}").json()["balance"])


# --- happy path: policy examples ------------------------------------------


@pytest.mark.parametrize(
    "amount,expected_fee",
    [
        ("3.00", "0.02"),
        ("10.10", "0.05"),
        ("100.00", "0.50"),
        ("999.99", "5.00"),
        ("1000.00", "2.50"),
        ("1234.56", "3.09"),
    ],
)
def test_fee_matches_policy_examples(amount, expected_fee):
    # Arrange
    _setup_pair()
    # Act
    resp = _transfer(amount)
    # Assert
    assert resp.status_code == 201
    assert D(resp.json()["fee"]) == D(expected_fee)


def test_fee_is_deducted_from_sender_balance():
    # Arrange
    _setup_pair(a="1000.00")
    # Act
    resp = _transfer("100.00")
    # Assert
    assert resp.status_code == 201
    assert _balance("A") == D("1000.00") - D("100.00") - D("0.50")
    assert _balance("B") == D("100.00")


# --- rounding (ROUND_HALF_UP) ---------------------------------------------


# Each raw fee lands exactly on a half cent, and the neighbouring cent below it is EVEN, so
# ROUND_HALF_EVEN (banker's rounding) would round DOWN while ROUND_HALF_UP rounds UP:
#   1.00 * 0.5% = 0.005 -> HALF_UP 0.01, banker's 0.00
#   5.00 * 0.5% = 0.025 -> HALF_UP 0.03, banker's 0.02
#   9.00 * 0.5% = 0.045 -> HALF_UP 0.05, banker's 0.04
# (3.00 -> 0.015 and 7.00 -> 0.035 give the same result under both methods, so they cannot
# distinguish them; 3.00 is already covered by the policy example table above.)
@pytest.mark.parametrize("amount,expected_fee", [("1.00", "0.01"), ("5.00", "0.03"), ("9.00", "0.05")])
def test_fee_rounds_half_up_at_half_cent(amount, expected_fee):
    # Arrange
    _setup_pair()
    # Act
    resp = _transfer(amount)
    # Assert
    assert resp.status_code == 201
    assert D(resp.json()["fee"]) == D(expected_fee)


# --- boundary: threshold 1000.00 inclusive ---------------------------------


@pytest.mark.parametrize(
    "amount,expected_fee",
    [("999.99", "5.00"), ("1000.00", "2.50"), ("1000.01", "2.50")],
)
def test_fee_rate_switches_at_threshold_inclusive(amount, expected_fee):
    # Arrange
    _setup_pair()
    # Act
    resp = _transfer(amount)
    # Assert
    assert resp.status_code == 201
    assert D(resp.json()["fee"]) == D(expected_fee)
    assert _balance("A") == D("100000.00") - D(amount) - D(expected_fee)


# --- negative / float precision -------------------------------------------


def test_fee_not_charged_when_transfer_rejected():
    # Arrange: 1000.00 + 2.50 needed, only 1002.49 available
    _setup_pair(a="1002.49")
    # Act
    resp = _transfer("1000.00")
    # Assert
    assert_error(resp, 409, "INSUFFICIENT_FUNDS")
    assert _balance("A") == D("1002.49")


def test_repeated_float_amount_transfers_keep_exact_cents():
    # Arrange
    _setup_pair(a="100.00")
    # Act: 0.1 sent as a JSON float; fee 0.0005 -> 0.00
    for _ in range(10):
        assert _transfer(0.1).status_code == 201
    # Assert
    assert _balance("A") == D("99.00")
    assert _balance("B") == D("1.00")
    raw = client.get("/accounts/A").text
    assert "99.00000" not in raw and "98.9999" not in raw
