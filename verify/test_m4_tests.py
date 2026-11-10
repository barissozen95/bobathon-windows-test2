"""M4 - Kapsamli test yazimi: aurora-pay-core icin test paketi (tests/)."""

import json
import logging
import os
import re
import sys
from decimal import Decimal

import pytest
from common import ROOT, run
from fastapi.testclient import TestClient

from services.core import store
from services.core.main import app

TESTS = ROOT / "tests"
VERIFY = ROOT / "verify"
OUT = ROOT / ".verify"
MIN_TESTS = 25
MIN_COVERAGE = 85.0
D = lambda v: Decimal(str(v))  # noqa: E731


def _pytest(extra: list[str], env: dict | None = None):
    OUT.mkdir(exist_ok=True)
    full_env = {"PYTHONPATH": f"{VERIFY}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"}
    full_env.update(env or {})
    return run(
        [sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider", "-W", "ignore", "-x", *extra],
        env=full_env,
        timeout=180,
    )


def _summary(result) -> str:
    lines = [ln for ln in (result.stdout + result.stderr).splitlines() if ln.strip()]
    failed = [ln for ln in lines if ln.startswith("FAILED")]
    if failed:
        return failed[0][:160]
    return lines[-1][:160] if lines else "cikti yok"


@pytest.fixture(scope="module")
def baseline():
    if not TESTS.exists() or not list(TESTS.glob("test_*.py")):
        pytest.fail("tests/ altinda test dosyasi yok", pytrace=False)
    cov_file = OUT / "coverage.json"
    if cov_file.exists():
        cov_file.unlink()
    result = _pytest(["--cov=services/core", "--cov-branch", f"--cov-report=json:{cov_file}"])
    return result, cov_file


# ---- Testlerin kendisi ----------------------------------------------------


def test_enough_tests_collected():
    """En az 25 test yazilmis"""
    result = run([sys.executable, "-m", "pytest", "tests", "--collect-only", "-q", "-p", "no:cacheprovider", "-W", "ignore"])
    match = re.search(r"(\d+) tests? collected", result.stdout) or re.search(r"^(\d+)/\d+|(\d+) test", result.stdout, re.M)
    count = len([ln for ln in result.stdout.splitlines() if "::" in ln])
    assert count >= MIN_TESTS, f"{count} test bulundu, en az {MIN_TESTS} gerekli ({match.group(0) if match else 'toplama hatasi'})"


def test_your_test_suite_passes(baseline):
    """Yazdiginiz testlerin tamami geciyor (bulduklariniz hatalari duzeltin)"""
    result, _ = baseline
    assert result.returncode == 0, f"basarisiz test var -> {_summary(result)}"


def test_coverage_threshold(baseline):
    """services/core satir kapsami en az %85"""
    result, cov_file = baseline
    assert cov_file.exists(), "kapsam raporu uretilemedi (testler gecmiyor olabilir)"
    percent = json.loads(cov_file.read_text())["totals"]["percent_covered"]
    assert percent >= MIN_COVERAGE, f"kapsam %{percent:.1f}, hedef %{MIN_COVERAGE:.0f}"


def test_tests_follow_team_standard():
    """Testler ekip standardina uyuyor (TestClient, store.reset, ic fonksiyon import'u yok)"""
    text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in TESTS.rglob("*.py"))
    assert "TestClient" in text, "API seviyesinde test yok: fastapi.testclient.TestClient kullanilmali"
    assert "store.reset" in text, "testler arasi izolasyon yok: her testten once store.reset() cagrilmali"
    internal = re.findall(r"^\s*from services\.core\.(service|fees|reports|errors) import", text, re.M)
    assert not internal, f"ic fonksiyon import'u var ({', '.join(sorted(set(internal)))}); testler API uzerinden yazilmali (ENGINEERING-HANDBOOK 4)"


# ---- Testler gercekten koruyor mu? (mutasyon) -------------------------------

MUTANTS = {
    "fee_threshold": "1000.00 esik degeri testi (>= sinirinda dusuk oran)",
    "fee_rounding": "ROUND_HALF_UP yuvarlama testi (3.00 -> 0.02)",
    "fee_not_charged": "ucretin bakiyeden dusuldugu testi",
    "idempotency_off": "ayni Idempotency-Key tekrar oynatma testi",
}


@pytest.mark.parametrize("name", list(MUTANTS))
def test_tests_catch_deliberate_bugs(baseline, name):
    """Testleriniz bilincli olarak bozulan kodu yakaliyor"""
    result, _ = baseline
    if result.returncode != 0:
        pytest.fail("once testlerinizin gecmesi gerekiyor", pytrace=False)
    report = OUT / f"mutant-{name}.txt"
    if report.exists():
        report.unlink()
    mutated = _pytest([], env={"MUTANT": name, "MUTANT_REPORT": str(report)} | {"PYTEST_ADDOPTS": "-p _mutants"})
    status = report.read_text() if report.exists() else "not-applicable"
    if status != "applied":
        pytest.skip(f"'{name}' kodunuza uygulanamadi (farkli yapi); eğitmen manuel bakar")
    assert mutated.returncode != 0, f"testleriniz bu bozulmayi fark etmedi: {MUTANTS[name]}"


# ---- Testlerle ortaya cikan gizli hatalar duzeltilmis mi? --------------------


@pytest.fixture
def client():
    store.reset()
    yield TestClient(app, raise_server_exceptions=False)
    store.reset()


def _acc(client, account_id, balance, owner="Test", iban=None):
    return client.post("/accounts", json={"id": account_id, "owner_name": owner, "iban": iban or f"TR00{account_id}", "balance": balance})


def _envelope(response, status, code):
    assert response.status_code == status, f"{status} beklendi, {response.status_code} geldi"
    assert response.json().get("error", {}).get("code") == code, f"'{code}' beklendi, gelen: {response.text[:100]}"


def test_hidden_bug_duplicate_account_does_not_overwrite(client):
    """Gizli hata 1: ayni id ile ikinci hesap mevcut hesabi ezmemeli (409 ACCOUNT_ALREADY_EXISTS)"""
    _acc(client, "A", 500)
    _envelope(_acc(client, "A", 1), 409, "ACCOUNT_ALREADY_EXISTS")
    assert D(client.get("/accounts/A").json()["balance"]) == D("500"), "mevcut hesabin bakiyesi ezildi"


def test_hidden_bug_negative_opening_balance_rejected(client):
    """Gizli hata 2: negatif acilis bakiyesi reddedilmeli (422 VALIDATION_ERROR)"""
    _envelope(_acc(client, "A", -10), 422, "VALIDATION_ERROR")


def test_hidden_bug_self_transfer_rejected(client):
    """Gizli hata 3: kendine transfer reddedilmeli ve bakiye degismemeli (422)"""
    _acc(client, "A", 1000)
    response = client.post("/transfers", json={"from_account": "A", "to_account": "A", "amount": 100})
    _envelope(response, 422, "VALIDATION_ERROR")
    assert D(client.get("/accounts/A").json()["balance"]) == D("1000"), "kendine transferde bakiye degisti"


def test_hidden_bug_logs_contain_no_pii(client, caplog):
    """Gizli hata 4: log'lara ad-soyad / IBAN yazilmamali (ENGINEERING-HANDBOOK 3)"""
    _acc(client, "A", 1000, owner="Ayse Demir", iban="TR544675118651433004071029")
    _acc(client, "B", 0, owner="Mehmet Arslan", iban="TR142771657106125823036929")
    with caplog.at_level(logging.DEBUG):
        client.post("/transfers", json={"from_account": "A", "to_account": "B", "amount": 100})
    leaked = [s for s in ("Ayse Demir", "Mehmet Arslan", "TR544675118651433004071029", "TR142771657106125823036929") if s in caplog.text]
    assert not leaked, f"log'da kisisel veri var: {leaked}"
