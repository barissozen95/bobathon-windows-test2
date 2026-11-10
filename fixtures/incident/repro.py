"""INCIDENT-2041 yeniden uretim betigi.

Kullanim (repo kokunden):  python fixtures/incident/repro.py
Cikis kodu: 0 = tum sikayetler giderilmis, 1 = en az biri hala mevcut.
"""

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient  # noqa: E402

from services.core import store  # noqa: E402
from services.core.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)


def _dec(value) -> Decimal:
    return Decimal(str(value))


def _setup(a_balance=1000, b_balance=0):
    store.reset()
    client.post("/accounts", json={"id": "A", "owner_name": "Test A", "iban": "TR000000000000000000000001", "balance": a_balance})
    client.post("/accounts", json={"id": "B", "owner_name": "Test B", "iban": "TR000000000000000000000002", "balance": b_balance})


def _balance(account_id):
    return _dec(client.get(f"/accounts/{account_id}").json()["balance"])


def check_1_idempotency():
    _setup()
    body = {"from_account": "A", "to_account": "B", "amount": 100}
    headers = {"Idempotency-Key": "k-1"}
    first = client.post("/transfers", json=body, headers=headers)
    second = client.post("/transfers", json=body, headers=headers)
    ok = (
        first.status_code == 201
        and second.status_code in (200, 201)
        and first.json().get("id") == second.json().get("id")
        and _balance("B") == Decimal("100")
    )
    return ok, "ayni Idempotency-Key ile iki istek tek borclandirma yapmali"


def check_2_atomicity():
    _setup()
    resp = client.post("/transfers", json={"from_account": "A", "to_account": "ACC-9999", "amount": 100})
    ok = resp.status_code == 404 and _balance("A") == Decimal("1000")
    return ok, "bilinmeyen alici: 404 donmeli ve gonderenin bakiyesi degismemeli"


def check_3_money():
    _setup(a_balance=100.10)
    client.post("/transfers", json={"from_account": "A", "to_account": "B", "amount": 10.10})
    exact = _balance("A") == Decimal("89.95")
    _setup(a_balance=10000)
    fees = {}
    for amount in (3, 1000):
        fees[amount] = _dec(
            client.post("/transfers", json={"from_account": "A", "to_account": "B", "amount": amount}).json().get("fee", -1)
        )
    ok = exact and fees[3] == Decimal("0.02") and fees[1000] == Decimal("2.50")
    return ok, "bakiye kurus hassasiyetinde tam olmali; ucret FEE-POLICY.md ile uyusmali"


def check_4_errors():
    _setup(a_balance=50)
    cases = [
        ({"from_account": "A", "to_account": "B", "amount": 500}, 409, "INSUFFICIENT_FUNDS"),
        ({"from_account": "A", "to_account": "B", "amount": -5}, 422, "VALIDATION_ERROR"),
        ({"from_account": "A"}, 422, "VALIDATION_ERROR"),
        ({"from_account": "NOPE", "to_account": "B", "amount": 1}, 404, "ACCOUNT_NOT_FOUND"),
    ]
    ok = True
    for body, status, code in cases:
        resp = client.post("/transfers", json=body)
        payload = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        if resp.status_code != status or payload.get("error", {}).get("code") != code:
            ok = False
    return ok, "hatalar el kitabindaki hata zarfi ve durum kodlariyla donmeli"


CHECKS = [
    ("Sikayet 1 - cift borclandirma", check_1_idempotency),
    ("Sikayet 2 - kayip para", check_2_atomicity),
    ("Sikayet 3 - kurus farklari", check_3_money),
    ("Sikayet 4 - hata yonetimi", check_4_errors),
]


def main() -> int:
    failed = 0
    for title, check in CHECKS:
        try:
            ok, hint = check()
        except Exception as exc:  # noqa: BLE001
            ok, hint = False, f"beklenmeyen istisna: {type(exc).__name__}"
        print(f"[{'PASS' if ok else 'FAIL'}] {title}")
        if not ok:
            print(f"       beklenen: {hint}")
            failed += 1
    print()
    print("INCIDENT-2041: " + ("COZULDU" if failed == 0 else f"{failed} sikayet acik"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
