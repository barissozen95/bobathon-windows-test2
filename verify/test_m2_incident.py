"""M2 - Uretim hatasi: INCIDENT-2041 (cift borclandirma, kayip para, kurus farklari, hata yonetimi)."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from services.core import store
from services.core.main import app

client = TestClient(app, raise_server_exceptions=False)
D = lambda v: Decimal(str(v))  # noqa: E731


@pytest.fixture(autouse=True)
def _fresh_store():
    store.reset()
    yield
    store.reset()


def _account(account_id, balance, owner="Test"):
    return client.post(
        "/accounts",
        json={"id": account_id, "owner_name": owner, "iban": f"TR00{account_id}", "balance": balance},
    )


def _balance(account_id):
    return D(client.get(f"/accounts/{account_id}").json()["balance"])


def _transfer(amount, src="A", dst="B", key=None):
    headers = {"Idempotency-Key": key} if key else {}
    return client.post("/transfers", json={"from_account": src, "to_account": dst, "amount": amount}, headers=headers)


def _assert_envelope(response, status, code):
    assert response.status_code == status, f"{status} beklendi, {response.status_code} geldi"
    body = response.json()
    assert "detail" not in body, "varsayilan {'detail': ...} govdesi donuyor; hata zarfi kullanilmali"
    assert body.get("error", {}).get("code") == code, f"'{code}' beklendi, gelen: {body}"
    assert body["error"].get("message"), "hata zarfinda 'message' bos"


# ---- Sikayet 1: idempotency ----------------------------------------------


def test_same_idempotency_key_charges_once():
    """Ayni Idempotency-Key ile iki istek yalniz bir kez borclandirir"""
    _account("A", 1000), _account("B", 0)
    first, second = _transfer(100, key="k-1"), _transfer(100, key="k-1")
    assert first.status_code == 201, f"ilk istek 201 olmali: {first.status_code}"
    assert second.status_code in (200, 201), f"ikinci istek basarili yanit donmeli: {second.status_code}"
    assert first.json()["id"] == second.json()["id"], "ikinci istek ayni transferi dondurmeli (yeni islem olusmamali)"
    assert _balance("B") == D("100"), f"alici 100 almali, {_balance('B')}"
    assert _balance("A") == D("899.50"), f"gonderen yalniz bir kez (100 + 0.50 ucret) borclanmali: {_balance('A')}"


def test_different_idempotency_keys_are_separate_transfers():
    """Farkli Idempotency-Key'ler ayri islem sayilir"""
    _account("A", 1000), _account("B", 0)
    _transfer(100, key="k-1"), _transfer(100, key="k-2")
    assert _balance("B") == D("200"), f"iki ayri islem beklenir, alici bakiyesi: {_balance('B')}"


def test_requests_without_key_are_not_deduplicated():
    """Anahtarsiz istekler tekilleştirilmez"""
    _account("A", 1000), _account("B", 0)
    _transfer(100), _transfer(100)
    assert _balance("B") == D("200")


# ---- Sikayet 2: kayip para / atomiklik -------------------------------------


def test_unknown_recipient_is_404_and_sender_untouched():
    """Bilinmeyen alici: 404 ACCOUNT_NOT_FOUND, gonderenin bakiyesi degismez"""
    _account("A", 1000)
    _assert_envelope(_transfer(100, dst="ACC-9999"), 404, "ACCOUNT_NOT_FOUND")
    assert _balance("A") == D("1000"), f"para kayboldu: gonderen bakiyesi {_balance('A')}"


def test_unknown_sender_is_404():
    """Bilinmeyen gonderen: 404 ACCOUNT_NOT_FOUND"""
    _account("B", 0)
    _assert_envelope(_transfer(100, src="NOPE"), 404, "ACCOUNT_NOT_FOUND")


def test_failed_transfer_leaves_no_transfer_record():
    """Basarisiz transfer kayit olusturmaz"""
    _account("A", 1000)
    _transfer(100, dst="ACC-9999")
    assert len(store.transfers) == 0, "basarisiz islem icin transfer kaydi olusmus"


# ---- Sikayet 3: para dogrulugu --------------------------------------------


def test_balances_are_exact_to_the_cent():
    """Bakiyeler kurus hassasiyetinde tam (89.95, kayan nokta artigi yok)"""
    _account("A", 100.10), _account("B", 0)
    _transfer(10.10)
    assert _balance("A") == D("89.95"), f"89.95 beklendi, gelen: {client.get('/accounts/A').json()['balance']!r}"
    assert _balance("B") == D("10.10"), f"10.10 beklendi, gelen: {client.get('/accounts/B').json()['balance']!r}"


def test_repeated_small_transfers_do_not_drift():
    """10 kucuk transferden sonra bakiye tam (0.10 x 10)"""
    _account("A", 100), _account("B", 0)
    for _ in range(10):
        _transfer(0.10)
    assert _balance("B") == D("1.00"), f"alici tam 1.00 olmali: {client.get('/accounts/B').json()['balance']!r}"
    assert _balance("A") == D("99.00"), f"gonderen tam 99.00 olmali (0.10 icin ucret 0.00): {client.get('/accounts/A').json()['balance']!r}"


@pytest.mark.parametrize(
    "amount,expected_fee",
    [("3.00", "0.02"), ("10.10", "0.05"), ("100.00", "0.50"), ("999.99", "5.00"), ("1000.00", "2.50"), ("1234.56", "3.09")],
)
def test_fee_matches_policy(amount, expected_fee):
    """Ucret FEE-POLICY.md ile ayni (esik dahil, ROUND_HALF_UP)"""
    _account("A", 10000), _account("B", 0)
    response = _transfer(float(amount))
    assert response.status_code == 201, response.text
    assert D(response.json()["fee"]) == D(expected_fee), f"{amount} icin ucret {expected_fee} olmali, {response.json()['fee']!r} geldi"


# ---- Sikayet 4: hata yonetimi ---------------------------------------------


def test_insufficient_funds_is_409_and_balance_unchanged():
    """Yetersiz bakiye: 409 INSUFFICIENT_FUNDS, bakiye degismez"""
    _account("A", 50), _account("B", 0)
    _assert_envelope(_transfer(500), 409, "INSUFFICIENT_FUNDS")
    assert _balance("A") == D("50") and _balance("B") == D("0")


def test_amount_covers_fee_boundary():
    """Bakiye tutari karsiliyor ama ucreti karsilamiyorsa reddedilir"""
    _account("A", 100), _account("B", 0)
    _assert_envelope(_transfer(100), 409, "INSUFFICIENT_FUNDS")


@pytest.mark.parametrize("payload", [{"amount": -5}, {"amount": 0}, {"amount": "abc"}, {"amount": 1.234}, {}])
def test_invalid_transfer_body_is_422(payload):
    """Gecersiz transfer govdesi: 422 VALIDATION_ERROR"""
    _account("A", 1000), _account("B", 0)
    body = {"from_account": "A", "to_account": "B", **payload}
    if not payload:
        body.pop("to_account")
    _assert_envelope(client.post("/transfers", json=body), 422, "VALIDATION_ERROR")


def test_not_found_responses_use_envelope():
    """Hesap ve transfer 404'leri hata zarfi kullanir"""
    _assert_envelope(client.get("/accounts/NOPE"), 404, "ACCOUNT_NOT_FOUND")
    _assert_envelope(client.get("/transfers/NOPE"), 404, "TRANSFER_NOT_FOUND")


def test_no_stack_trace_or_internal_message_leaks():
    """Hicbir hata yanitinda stack trace veya ic hata mesaji yok"""
    _account("A", 10), _account("B", 0)
    for response in (_transfer(500), _transfer(1, dst="X"), client.post("/transfers", json={})):
        text = response.text
        assert "Traceback" not in text and "KeyError" not in text and 'File "' not in text, f"sizinti: {text[:120]}"


# ---- Gerileme (regression) -----------------------------------------------


def test_successful_transfer_still_works():
    """Basarili transfer hala calisiyor (alanlar, 201, bakiyeler)"""
    _account("A", 1000), _account("B", 5)
    response = _transfer(100)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "COMPLETED" and body["from_account"] == "A" and body["to_account"] == "B"
    assert D(body["amount"]) == D("100") and D(body["fee"]) == D("0.50")
    assert _balance("A") == D("899.50") and _balance("B") == D("105")
    assert client.get(f"/transfers/{body['id']}").status_code == 200
