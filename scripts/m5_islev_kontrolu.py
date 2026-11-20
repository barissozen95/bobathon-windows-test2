"""M5 islev kontrolu: guvenlik duzeltmesi gecerli girdiyi bozmadi mi?

Calistirma (repo kokunden):  python3 scripts/m5_islev_kontrolu.py   (Windows: py scripts/m5_islev_kontrolu.py)

Beklenen sonuc:
  gecerli arsiv adi  -> {'exit_code': 0}
  gecersiz arsiv adi -> HTTP 422
  SQL injection      -> []
Gecersiz ad denemeleri gecici bir dizinde calisir, repoda artik birakmaz.
"""

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from fastapi.testclient import TestClient  # noqa: E402

from services.core import store  # noqa: E402
from services.core.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)
store.reset()
ok = True


def report(label: str, passed: bool, detail: str) -> None:
    global ok
    ok = ok and passed
    print(f"[{'OK' if passed else 'HATA'}] {label}: {detail}")


# 1) Gecerli arsiv adi
(ROOT / "archives").mkdir(exist_ok=True)
target = ROOT / "archives" / "q1-2025.tgz"
response = client.post("/reports/archive", json={"filename": "q1-2025"})
report("Gecerli arsiv adi (q1-2025)", response.status_code == 200 and response.json() == {"exit_code": 0}, f"{response.status_code} {response.text}")
target.unlink(missing_ok=True)

# 2) Gecersiz arsiv adlari (gecici dizinde)
with tempfile.TemporaryDirectory() as tmp:
    os.chdir(tmp)
    for name in ["x; touch PWNED", "$(touch PWNED)", "../../etc/evil", "a b"]:
        response = client.post("/reports/archive", json={"filename": name})
        report(f"Gecersiz arsiv adi ({name!r})", response.status_code == 422, f"HTTP {response.status_code}")
    os.chdir(ROOT)

# 3) SQL injection
client.post("/accounts", json={"id": "A", "owner_name": "Alice", "iban": "TR1", "balance": 1000})
client.post("/accounts", json={"id": "B", "owner_name": "Bob", "iban": "TR2", "balance": 0})
client.post("/transfers", json={"from_account": "A", "to_account": "B", "amount": 10})
legit = client.get("/reports/transfers", params={"owner": "Alice"})
report("Mesru sorgu (owner=Alice)", legit.status_code == 200 and len(legit.json()) == 1, f"{len(legit.json())} kayit")
attack = client.get("/reports/transfers", params={"owner": "x' OR '1'='1"})
report("SQL injection denemesi", attack.json() == [], f"{len(attack.json())} kayit dondu")

store.reset()
print("\nSonuc:", "islev bozulmadi" if ok else "en az bir kontrol basarisiz")
sys.exit(0 if ok else 1)
