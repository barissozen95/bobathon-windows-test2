"""API tests for the Limits & Statements service (docs/PRD-limits.md)."""

import pytest
from fastapi.testclient import TestClient

from services.limits import store
from services.limits.main import app

client = TestClient(app)
CID = "C004217"


@pytest.fixture(autouse=True)
def _reset_store():
    store.reset()


def _put(cid=CID, daily="5000.00", per="2000.00"):
    return client.put(f"/limits/{cid}", json={"daily_limit": daily, "per_transfer_limit": per})


def _auth(amount, day="2025-03-14", cid=CID, description=None):
    return client.post(f"/limits/{cid}/authorize",
                       json={"amount": amount, "occurred_on": day, "description": description})


def _assert_validation_error(resp):
    assert resp.status_code == 422
    body = resp.json()
    assert "detail" not in body
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"]


# --- limits ---------------------------------------------------------------

def test_get_limits_returns_defaults_when_undefined():
    # Act
    resp = client.get(f"/limits/{CID}")
    # Assert
    assert resp.status_code == 200
    assert resp.json() == {"customer_id": CID, "daily_limit": "10000.00",
                           "per_transfer_limit": "5000.00", "source": "default"}


def test_put_limits_normalizes_amounts_to_two_decimals():
    # Act
    resp = _put(daily="5000", per="2000.5")
    # Assert
    assert resp.status_code == 200
    assert resp.json() == {"customer_id": CID, "daily_limit": "5000.00",
                           "per_transfer_limit": "2000.50", "source": "custom"}
    assert client.get(f"/limits/{CID}").json()["source"] == "custom"


def test_put_limits_accepts_per_transfer_equal_to_daily():
    assert _put(daily="3000.00", per="3000.00").status_code == 200


@pytest.mark.parametrize("daily,per", [
    ("1000.00", "1000.01"),   # per > daily
    ("0", "0"),               # zero
    ("1000.00", "0.00"),
    ("-5", "1"),              # negative
    ("100.123", "10"),        # 3 decimals
    ("abc", "10"),
    ("1e3", "10"),
])
def test_put_limits_rejects_invalid_values(daily, per):
    _assert_validation_error(_put(daily=daily, per=per))


@pytest.mark.parametrize("payload", [
    {"daily_limit": "1000"},
    {"daily_limit": 1000, "per_transfer_limit": 500},
    {},
])
def test_put_limits_rejects_malformed_body(payload):
    _assert_validation_error(client.put(f"/limits/{CID}", json=payload))


def test_put_limits_rejects_non_json_body():
    resp = client.put(f"/limits/{CID}", content=b"not json", headers={"content-type": "application/json"})
    _assert_validation_error(resp)


@pytest.mark.parametrize("cid", ["C12345", "C1234567", "c004217", "X004217", "C00421A"])
def test_endpoints_reject_invalid_customer_id(cid):
    _assert_validation_error(client.get(f"/limits/{cid}"))
    _assert_validation_error(_put(cid=cid))
    _assert_validation_error(_auth("10", cid=cid))
    _assert_validation_error(client.get(f"/statements/{cid}?from=2025-01-01&to=2025-01-02"))


# --- authorize --------------------------------------------------------------

def test_authorize_follows_prd_example_scenario():
    # Arrange
    _put()
    expected = [
        ("1500.00", "2025-03-14", True, None, "3500.00"),
        ("2500.00", "2025-03-14", False, "PER_TRANSFER_LIMIT_EXCEEDED", "3500.00"),
        ("2000.00", "2025-03-14", True, None, "1500.00"),
        ("1600.00", "2025-03-14", False, "DAILY_LIMIT_EXCEEDED", "1500.00"),
        ("1600.00", "2025-03-15", True, None, "3400.00"),
    ]
    for amount, day, allowed, reason, remaining in expected:
        # Act
        resp = _auth(amount, day)
        # Assert
        assert resp.status_code == 200
        assert resp.json() == {"customer_id": CID, "allowed": allowed,
                               "reason": reason, "remaining_daily": remaining}


def test_authorize_allows_amounts_exactly_at_limits():
    _put(daily="3000.00", per="2000.00")
    assert _auth("2000.00").json()["allowed"] is True
    resp = _auth("1000")
    assert resp.json() == {"customer_id": CID, "allowed": True, "reason": None, "remaining_daily": "0.00"}


def test_authorize_rejects_one_cent_over_limits():
    _put(daily="3000.00", per="2000.00")
    assert _auth("2000.01").json()["reason"] == "PER_TRANSFER_LIMIT_EXCEEDED"
    _auth("2000.00")
    assert _auth("1000.01").json()["reason"] == "DAILY_LIMIT_EXCEEDED"


def test_authorize_prefers_per_transfer_reason_when_both_exceeded():
    _put(daily="3000.00", per="2000.00")
    _auth("2000.00")
    assert _auth("2500.00").json()["reason"] == "PER_TRANSFER_LIMIT_EXCEEDED"


def test_authorize_uses_default_limits_when_undefined():
    assert _auth("5000.00").json() == {"customer_id": CID, "allowed": True,
                                       "reason": None, "remaining_daily": "5000.00"}
    assert _auth("5000.01").json()["reason"] == "PER_TRANSFER_LIMIT_EXCEEDED"


def test_authorize_rejected_transfer_does_not_consume_usage():
    _put(daily="1000.00", per="1000.00")
    _auth("600")
    assert _auth("500").json()["allowed"] is False
    assert _auth("400").json()["remaining_daily"] == "0.00"


def test_authorize_sums_decimals_exactly():
    for _ in range(3):
        resp = _auth("0.10")
    assert resp.json()["remaining_daily"] == "9999.70"


def test_authorize_usage_is_isolated_per_customer():
    _auth("5000", cid="C000001")
    assert _auth("5000", cid="C000002").json()["remaining_daily"] == "5000.00"


def test_limit_change_keeps_existing_usage():
    _put(daily="5000.00", per="2000.00")
    _auth("2000.00")
    assert _put(daily="3000.00", per="1000.00").status_code == 200
    assert _auth("1000.00").json() == {"customer_id": CID, "allowed": True,
                                       "reason": None, "remaining_daily": "0.00"}


def test_authorize_remaining_is_zero_when_lowered_limit_below_usage():
    _put(daily="5000.00", per="2000.00")
    _auth("2000.00")
    _auth("2000.00")
    _put(daily="1000.00", per="500.00")
    assert _auth("100").json() == {"customer_id": CID, "allowed": False,
                                   "reason": "DAILY_LIMIT_EXCEEDED", "remaining_daily": "0.00"}


@pytest.mark.parametrize("payload", [
    {"amount": "0", "occurred_on": "2025-03-14"},
    {"amount": "-10", "occurred_on": "2025-03-14"},
    {"amount": "100.123", "occurred_on": "2025-03-14"},
    {"amount": 100, "occurred_on": "2025-03-14"},
    {"amount": "100", "occurred_on": "14-03-2025"},
    {"amount": "100", "occurred_on": "2025-02-30"},
    {"amount": "100", "occurred_on": "20250314"},
    {"amount": "100"},
    {"occurred_on": "2025-03-14"},
])
def test_authorize_rejects_invalid_input(payload):
    _assert_validation_error(client.post(f"/limits/{CID}/authorize", json=payload))


# --- statements ---------------------------------------------------------------

def test_statement_lists_only_approved_entries_in_order():
    # Arrange
    _put()
    _auth("1600.00", "2025-03-15", description="d")
    _auth("1500.00", "2025-03-14", description="a")
    _auth("2500.00", "2025-03-14", description="rejected")
    _auth("2000.00", "2025-03-14", description="b")
    _auth("1600.00", "2025-03-14", description="rejected")
    # Act
    resp = client.get(f"/statements/{CID}?from=2025-03-14&to=2025-03-15")
    # Assert
    assert resp.status_code == 200
    assert resp.json() == {
        "customer_id": CID, "from": "2025-03-14", "to": "2025-03-15",
        "entries": [
            {"occurred_on": "2025-03-14", "amount": "1500.00", "description": "a"},
            {"occurred_on": "2025-03-14", "amount": "2000.00", "description": "b"},
            {"occurred_on": "2025-03-15", "amount": "1600.00", "description": "d"},
        ],
        "total": "5100.00",
    }


def test_statement_range_is_inclusive_on_both_ends():
    for day in ("2025-03-13", "2025-03-14", "2025-03-15", "2025-03-16"):
        _auth("10", day)
    resp = client.get(f"/statements/{CID}?from=2025-03-14&to=2025-03-15")
    assert [e["occurred_on"] for e in resp.json()["entries"]] == ["2025-03-14", "2025-03-15"]
    single = client.get(f"/statements/{CID}?from=2025-03-14&to=2025-03-14").json()
    assert single["total"] == "10.00"


def test_statement_is_empty_for_customer_without_transactions():
    resp = client.get(f"/statements/{CID}?from=2025-01-01&to=2025-12-31")
    assert resp.status_code == 200
    assert resp.json() == {"customer_id": CID, "from": "2025-01-01", "to": "2025-12-31",
                           "entries": [], "total": "0.00"}


@pytest.mark.parametrize("query", [
    "from=2025-03-15&to=2025-03-14",
    "from=2025-03-14",
    "to=2025-03-14",
    "",
    "from=2025/03/14&to=2025-03-15",
    "from=2025-13-01&to=2025-12-31",
])
def test_statement_rejects_invalid_range(query):
    _assert_validation_error(client.get(f"/statements/{CID}?{query}"))


def test_unknown_route_uses_error_envelope():
    resp = client.get("/nope")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"
