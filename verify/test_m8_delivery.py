"""M8 - Teslimat: dal, commit'ler, GitHub'a push ve Pull Request.

Bu kontroller GitHub'a erismez; yerel git durumuna ve dosyalara bakar. PR'in acik oldugunu
`gh` kuruluysa dogrular, degilse manuel kontrol (SKIP) olarak isaretler.
"""

import json
import re
import shutil

import pytest
from common import run

BASE_BRANCHES = {"main", "master"}


def _git(*args):
    return run(["git", *args])


def _branch():
    return _git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def test_work_is_on_a_feature_branch():
    """Calisma main'de degil, feature/ veya fix/ dalinda"""
    branch = _branch()
    assert branch not in BASE_BRANCHES, f"main dalindasiniz; 'feature/...' veya 'fix/...' dali acin (su an: {branch})"
    assert re.match(r"^(feature|fix)/[a-z0-9][a-z0-9._-]*$", branch), f"dal adi 'feature/<kisa-ad>' veya 'fix/<kisa-ad>' olmali (su an: {branch})"


def test_work_tree_is_clean():
    """Tum degisiklikler commit edilmis"""
    status = _git("status", "--porcelain").stdout.strip()
    dirty = [ln for ln in status.splitlines() if not ln[3:].startswith((".verify", "archives/"))]
    assert not dirty, f"commit edilmemis degisiklik var: {dirty[0][:60]}"


def test_commit_history_is_meaningful():
    """Dalda en az 3 anlamli commit var (tek 'update' degil)"""
    base = next((b for b in ("origin/main", "main", "origin/master", "master") if _git("rev-parse", "--verify", b).returncode == 0), None)
    assert base, "main dali bulunamadi"
    messages = [m for m in _git("log", f"{base}..HEAD", "--format=%s").stdout.splitlines() if m.strip()]
    assert len(messages) >= 3, f"dalda {len(messages)} commit var, en az 3 gerekli (gorev basina bir commit onerilir)"
    weak = [m for m in messages if len(m) < 12 or m.lower().strip(".") in {"update", "fix", "changes", "wip", "commit", "test"}]
    assert not weak, f"anlamsiz commit mesaji: {weak[0]!r} (ne yaptigini anlatan bir cumle yazin)"


def test_branch_pushed_to_github():
    """Dal GitHub'a (origin) push edilmis"""
    remote = _git("remote", "get-url", "origin")
    assert remote.returncode == 0, "'origin' remote'u yok (sablondan olusturdugunuz depoyu klonladiniz mi?)"
    assert "github" in remote.stdout, f"origin GitHub degil: {remote.stdout.strip()}"
    branch = _branch()
    local = _git("rev-parse", "HEAD").stdout.strip()
    remote_head = _git("rev-parse", f"origin/{branch}")
    assert remote_head.returncode == 0, f"origin/{branch} yok -> git push -u origin {branch}"
    assert remote_head.stdout.strip() == local, "yerel commit'ler push edilmemis"


def test_pull_request_is_open():
    """Dal icin acik bir Pull Request var (gh ile dogrulanir)"""
    if not shutil.which("gh"):
        pytest.skip("'gh' kurulu degil; PR'i facilitator'a gosterin")
    result = run(["gh", "pr", "view", "--json", "state,title,body,url"])
    if result.returncode != 0:
        pytest.fail("bu dal icin Pull Request bulunamadi (veya gh giris yapmamis: gh auth status)", pytrace=False)
    pr = json.loads(result.stdout)
    assert pr["state"] == "OPEN", f"PR durumu {pr['state']}"
    assert len(pr["title"]) >= 10, "PR basligi cok kisa"
    body = pr["body"] or ""
    assert len(body.strip()) >= 80, "PR aciklamasi cok kisa; sablonu doldurun"
    assert "- [x]" in body.lower(), "PR sablonundaki kontrol listesini isaretleyin (en az bir '- [x]')"


def test_ci_workflow_is_green():
    """PR'daki CI kontrolleri basarili (gh pr checks)"""
    if not shutil.which("gh"):
        pytest.skip("'gh' kurulu degil; CI sonucunu facilitator'a gosterin")
    result = run(["gh", "pr", "checks", "--json", "name,state"])
    if result.returncode not in (0, 8):
        pytest.fail("PR kontrolleri okunamadi (PR acik mi?)", pytrace=False)
    checks = json.loads(result.stdout or "[]")
    assert checks, "PR icin CI kontrolu bulunamadi; .github/workflows/ci.yml push edildi mi?"
    bad = [c["name"] for c in checks if c["state"] not in ("SUCCESS", "SKIPPED")]
    assert not bad, f"basarisiz/bekleyen kontrol: {bad} (gh pr checks --watch)"
