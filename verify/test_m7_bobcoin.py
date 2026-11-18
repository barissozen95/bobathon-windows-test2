"""M7 - Bobcoin ve analytics: tuketimi olc, siniri ayarla, yorumla (reports/)."""

import json
import re

from common import ROOT

RUN_JSON = ROOT / "reports" / "bob-run.json"
NOTES = ROOT / "reports" / "bobcoin-notes.md"


def _json_documents(text: str):
    """Tek bir JSON belgesi veya satir basina bir JSON (stream-json) kabul eder."""
    try:
        return [json.loads(text)]
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]


def test_bounded_run_output_saved():
    """reports/bob-run.json: 'bob run --format json' ciktisi gecerli JSON"""
    assert RUN_JSON.exists(), "reports/bob-run.json yok -> bob run --format json ... > reports/bob-run.json"
    text = RUN_JSON.read_text(encoding="utf-8", errors="replace").strip()
    assert len(text) >= 50, "cikti cok kisa; bob run gercekten calisti mi?"
    try:
        docs = _json_documents(text)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"gecerli JSON degil ({exc.msg}); '--format json' kullandiniz mi?") from None
    assert docs, "JSON belgesi yok"
    results = [d for d in docs if isinstance(d, dict) and d.get("type") == "result"]
    assert results, "'\"type\": \"result\"' iceren JSON belgesi yok; bu dosya gercek bir 'bob run --format json' ciktisi degil"
    costs = [
        d["stats"]["session_costs"]
        for d in results
        if isinstance(d.get("stats"), dict)
        and isinstance(d["stats"].get("session_costs"), (int, float))
        and not isinstance(d["stats"]["session_costs"], bool)
    ]
    assert costs, "result belgesinde 'stats.session_costs' (sayi) yok; bu dosya gercek bir 'bob run --format json' ciktisi degil"


def test_notes_have_real_numbers():
    """reports/bobcoin-notes.md: Bobcoin rakamlari ve kaynaklari (portal / Bobalytics) yazilmis"""
    assert NOTES.exists(), "reports/bobcoin-notes.md yok"
    text = NOTES.read_text(encoding="utf-8", errors="replace")
    low = text.lower()
    assert len(text.strip()) >= 200, "notlar cok kisa (en az ~200 karakter)"
    assert "bobcoin" in low, "'Bobcoin' gecmiyor"
    assert re.search(r"\d+([.,]\d+)?", text), "hicbir rakam yok; gordugunuz degerleri yazin"
    assert any(w in low for w in ("bobalytics", "admin", "portal", "dashboard")), "rakamlari nereden okudugunuzu yazin (portal / Bobalytics)"


def test_notes_explain_budget_decision():
    """Notlar bir butce karari iceriyor (--max-cost / --max-turns / oneri)"""
    low = NOTES.read_text(encoding="utf-8", errors="replace").lower() if NOTES.exists() else ""
    assert any(w in low for w in ("max-cost", "max-turns", "limit", "sinir", "butce", "bütçe", "oneri", "öneri")), (
        "notlarda bir butce/sinir onerisi yok (ornegin: 'bu is icin --max-cost 0.5 yeterli')"
    )
