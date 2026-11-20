"""M1 - Dokumandan koda: Limits & Statements servisi (PRD-limits.md + API-SPEC-limits.yaml)."""

import pytest
from common import next_customer_id

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="module")
def client():
    try:
        from services.limits.main import app
    except ImportError as exc:
        pytest.fail(f"services/limits/main.py icinde 'app' bulunamadi ({exc})", pytrace=False)
    return TestClient(app, raise_server_exceptions=False)


def _authorize(client, cid, amount, day="2025-03-14", description=None):
    body = {"amount": amount, "occurred_on": day}
    if description is not None:
        body["description"] = description
    return client.post(f"/limits/{cid}/authorize", json=body)


def _set_limits(client, cid, daily, per):
    return client.put(f"/limits/{cid}", json={"daily_limit": daily, "per_transfer_limit": per})


def _assert_validation_error(response):
    assert response.status_code == 422, f"422 beklendi, {response.status_code} geldi"
    body = response.json()
    assert "detail" not in body, "FastAPI varsayilan {'detail': ...} govdesi donuyor; hata zarfi kullanilmali"
    assert body.get("error", {}).get("code") == "VALIDATION_ERROR", f"hata zarfi beklendi, gelen: {body}"
    assert body["error"].get("message"), "hata zarfinda 'message' bos"


# ---- Limitler -------------------------------------------------------------


def test_default_limits_for_unknown_customer(client):
    """Tanimsiz musteri icin varsayilan limitler (10000.00 / 5000.00)"""
    cid = next_customer_id()
    response = client.get(f"/limits/{cid}")
    assert response.status_code == 200
    body = response.json()
    assert body["customer_id"] == cid
    assert body["daily_limit"] == "10000.00" and body["per_transfer_limit"] == "5000.00", f"varsayilanlar hatali: {body}"
    assert body["source"] == "default"


def test_put_then_get_limits_roundtrip(client):
    """Limit tanimla ve geri oku (ondalik kismi olmayan veya 1 ondalikli tutar da gecerli; yanit 2 ondalikli, source=custom)"""
    cid = next_customer_id()
    put = _set_limits(client, cid, "5000", "2000.5")
    assert put.status_code == 200, put.text
    body = client.get(f"/limits/{cid}").json()
    assert body["daily_limit"] == "5000.00" and body["per_transfer_limit"] == "2000.50", f"2 ondalik bicimi hatali: {body}"
    assert body["source"] == "custom"


@pytest.mark.parametrize(
    "daily,per",
    [
        ("1000.00", "2000.00"),  # per > daily
        ("0", "0"),
        ("-5", "-5"),
        ("100.123", "50"),  # 3 ondalik
        ("abc", "10"),
        ("", "10"),
    ],
)
def test_put_invalid_limits_return_error_envelope(client, daily, per):
    """Gecersiz limit degerleri 422 + hata zarfi doner"""
    _assert_validation_error(_set_limits(client, next_customer_id(), daily, per))


def test_put_missing_field_returns_error_envelope(client):
    """Eksik alan 422 + hata zarfi doner"""
    response = client.put(f"/limits/{next_customer_id()}", json={"daily_limit": "100.00"})
    _assert_validation_error(response)


@pytest.mark.parametrize("bad_id", ["X123456", "C12345", "C1234567", "c123456", "C12345A"])
def test_invalid_customer_id_is_rejected(client, bad_id):
    """Gecersiz customer_id bicimi 422 doner"""
    _assert_validation_error(client.get(f"/limits/{bad_id}"))


# ---- Yetkilendirme --------------------------------------------------------


def test_authorize_within_limits_is_allowed(client):
    """Limit icindeki islem onaylanir, kalan gunluk tutar doner"""
    cid = next_customer_id()
    _set_limits(client, cid, "5000.00", "2000.00")
    response = _authorize(client, cid, "1500.00")
    assert response.status_code == 200
    body = response.json()
    assert body["allowed"] is True and body.get("reason") is None, body
    assert body["remaining_daily"] == "3500.00", f"kalan gunluk 3500.00 olmali, gelen: {body['remaining_daily']}"


def test_per_transfer_limit_exceeded(client):
    """Islem basina limit asimi: PER_TRANSFER_LIMIT_EXCEEDED"""
    cid = next_customer_id()
    _set_limits(client, cid, "5000.00", "2000.00")
    body = _authorize(client, cid, "2000.01").json()
    assert body["allowed"] is False and body["reason"] == "PER_TRANSFER_LIMIT_EXCEEDED", body


def test_daily_limit_exceeded(client):
    """Gunluk limit asimi: DAILY_LIMIT_EXCEEDED"""
    cid = next_customer_id()
    _set_limits(client, cid, "3000.00", "2000.00")
    assert _authorize(client, cid, "2000.00").json()["allowed"] is True
    body = _authorize(client, cid, "1000.01").json()
    assert body["allowed"] is False and body["reason"] == "DAILY_LIMIT_EXCEEDED", body


def test_per_transfer_reason_has_priority(client):
    """Iki limit de asilirsa PER_TRANSFER_LIMIT_EXCEEDED oncelikli"""
    cid = next_customer_id()
    _set_limits(client, cid, "3000.00", "1000.00")
    _authorize(client, cid, "1000.00")
    _authorize(client, cid, "1000.00")
    body = _authorize(client, cid, "2500.00").json()
    assert body["reason"] == "PER_TRANSFER_LIMIT_EXCEEDED", f"oncelik kurali: {body}"


def test_limits_are_inclusive(client):
    """Tam limite esit tutar onaylanir (dahil)"""
    cid = next_customer_id()
    _set_limits(client, cid, "2000.00", "2000.00")
    first = _authorize(client, cid, "2000.00").json()
    assert first["allowed"] is True and first["remaining_daily"] == "0.00", f"tam limit onaylanmali: {first}"
    second = _authorize(client, cid, "0.01").json()
    assert second["allowed"] is False and second["reason"] == "DAILY_LIMIT_EXCEEDED", second


def test_rejected_transfers_do_not_consume_usage(client):
    """Reddedilen islem kullanima yazilmaz"""
    cid = next_customer_id()
    _set_limits(client, cid, "5000.00", "2000.00")
    _authorize(client, cid, "1500.00")
    _authorize(client, cid, "2500.00")  # red
    body = _authorize(client, cid, "2000.00").json()
    assert body["allowed"] is True and body["remaining_daily"] == "1500.00", f"red kullanimi etkilememeli: {body}"


def test_usage_is_independent_across_days(client):
    """Kullanim gunler arasinda bagimsiz"""
    cid = next_customer_id()
    _set_limits(client, cid, "5000.00", "2000.00")
    _authorize(client, cid, "2000.00", day="2025-03-14")
    _authorize(client, cid, "2000.00", day="2025-03-14")
    body = _authorize(client, cid, "1600.00", day="2025-03-15").json()
    assert body["allowed"] is True and body["remaining_daily"] == "3400.00", f"ertesi gun bagimsiz olmali: {body}"


def test_limit_change_keeps_existing_usage(client):
    """Limit degisikligi gecmis kullanimi silmez"""
    cid = next_customer_id()
    _set_limits(client, cid, "5000.00", "2000.00")
    _authorize(client, cid, "2000.00")
    _set_limits(client, cid, "6000.00", "3000.00")
    body = _authorize(client, cid, "1000.00").json()
    assert body["allowed"] is True and body["remaining_daily"] == "3000.00", f"6000 - 2000 - 1000 = 3000 beklenir: {body}"


def test_default_limits_apply_when_not_configured(client):
    """Tanimsiz musteri varsayilan limitle yetkilendirilir"""
    cid = next_customer_id()
    assert _authorize(client, cid, "5000.00").json()["allowed"] is True
    body = _authorize(client, cid, "5000.01").json()
    assert body["reason"] == "PER_TRANSFER_LIMIT_EXCEEDED", body


def test_no_float_rounding_errors(client):
    """Para float ile hesaplanmaz (0.10 x 3 = 0.30 tam olmali)"""
    cid = next_customer_id()
    _set_limits(client, cid, "0.30", "0.30")
    results = [_authorize(client, cid, "0.10").json() for _ in range(4)]
    assert [r["allowed"] for r in results] == [True, True, True, False], f"float hatasi: {[r['allowed'] for r in results]}"
    assert results[2]["remaining_daily"] == "0.00", f"kalan 0.00 olmali: {results[2]['remaining_daily']}"


@pytest.mark.parametrize("amount", ["0", "-1.00", "abc", "10.999", ""])
def test_authorize_invalid_amount(client, amount):
    """Gecersiz tutar 422 + hata zarfi doner"""
    cid = next_customer_id()
    _assert_validation_error(_authorize(client, cid, amount))


def test_authorize_invalid_date(client):
    """Gecersiz tarih 422 + hata zarfi doner"""
    cid = next_customer_id()
    _assert_validation_error(_authorize(client, cid, "10.00", day="2025-13-45"))


# ---- Statement ------------------------------------------------------------


def test_statement_lists_only_approved_in_order_with_total(client):
    """Statement: yalniz onaylananlar, tarihe gore sirali, toplam dogru"""
    cid = next_customer_id()
    _set_limits(client, cid, "5000.00", "2000.00")
    _authorize(client, cid, "1500.00", day="2025-03-14", description="kira")
    _authorize(client, cid, "2500.00", day="2025-03-14", description="red")  # red
    _authorize(client, cid, "2000.00", day="2025-03-14", description="fatura")
    _authorize(client, cid, "1600.00", day="2025-03-15", description="market")
    _authorize(client, cid, "100.00", day="2025-03-13", description="erken")

    response = client.get(f"/statements/{cid}", params={"from": "2025-03-13", "to": "2025-03-15"})
    assert response.status_code == 200
    body = response.json()
    assert [e["description"] for e in body["entries"]] == ["erken", "kira", "fatura", "market"], (
        f"siralama/icerik hatali: {[e.get('description') for e in body['entries']]}"
    )
    assert [e["amount"] for e in body["entries"]] == ["100.00", "1500.00", "2000.00", "1600.00"]
    assert body["total"] == "5200.00", f"toplam 5200.00 olmali: {body['total']}"
    assert body["from"] == "2025-03-13" and body["to"] == "2025-03-15"


def test_statement_range_is_inclusive_and_filters(client):
    """Statement tarih araligi uclar dahil, disarisini icermez"""
    cid = next_customer_id()
    _set_limits(client, cid, "5000.00", "2000.00")
    for day in ("2025-03-13", "2025-03-14", "2025-03-15", "2025-03-16"):
        _authorize(client, cid, "100.00", day=day)
    body = client.get(f"/statements/{cid}", params={"from": "2025-03-14", "to": "2025-03-15"}).json()
    assert [e["occurred_on"] for e in body["entries"]] == ["2025-03-14", "2025-03-15"], body["entries"]
    assert body["total"] == "200.00"


def test_statement_empty_for_customer_without_transfers(client):
    """Islemi olmayan musteri icin bos statement (hata degil)"""
    response = client.get(f"/statements/{next_customer_id()}", params={"from": "2025-01-01", "to": "2025-12-31"})
    assert response.status_code == 200
    body = response.json()
    assert body["entries"] == [] and body["total"] == "0.00", body


def test_statement_from_after_to_is_invalid(client):
    """from > to gecersiz (422 + hata zarfi)"""
    _assert_validation_error(client.get(f"/statements/{next_customer_id()}", params={"from": "2025-03-15", "to": "2025-03-14"}))


def test_statement_missing_or_bad_dates(client):
    """Eksik veya bozuk tarih parametresi 422 + hata zarfi"""
    cid = next_customer_id()
    _assert_validation_error(client.get(f"/statements/{cid}", params={"from": "2025-03-14"}))
    _assert_validation_error(client.get(f"/statements/{cid}", params={"from": "bugun", "to": "yarin"}))
