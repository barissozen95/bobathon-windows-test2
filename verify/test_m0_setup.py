"""M0 - Kurulum kontrolleri."""

import importlib
import shutil
import sys

import pytest
from common import ROOT, run

SETUP_HINT = "python3 setup.py --scanners  (Windows: py setup.py --scanners)"


def _find_semgrep():
    for folder in (".venv-tools/bin", ".venv-tools/Scripts", ".venv/bin", ".venv/Scripts"):
        for exe in ("semgrep", "semgrep.exe"):
            candidate = ROOT / folder / exe
            if candidate.exists():
                return str(candidate)
    return shutil.which("semgrep")


def test_python_version():
    """Python 3.11 veya uzeri"""
    assert sys.version_info >= (3, 11), (
        f"Python {sys.version_info.major}.{sys.version_info.minor} bulundu, 3.11+ gerekli. "
        "Yeni bir Python kurup kurulumu onunla calistirin (ornek: PYTHON=/yol/python3.12 ./setup.sh --scanners)"
    )


def test_dependencies_installed():
    """Bagimliliklar kurulu (fastapi, pytest, httpx, yaml)"""
    missing = []
    for name in ("fastapi", "pytest", "httpx", "yaml", "pytest_cov"):
        try:
            importlib.import_module(name)
        except ImportError:
            missing.append(name)
    assert not missing, f"eksik paket: {', '.join(missing)}  ->  {SETUP_HINT}"


def test_core_app_boots():
    """Aurora Core uygulamasi ayaga kalkiyor (/health)"""
    from fastapi.testclient import TestClient

    from services.core.main import app

    response = TestClient(app).get("/health")
    assert response.status_code == 200 and response.json() == {"status": "ok"}, "/health beklenen yaniti vermedi"


def test_repo_has_workshop_files():
    """Gorev dosyalari yerinde (docs, fixtures, deploy)"""
    expected = [
        "docs/PRD-limits.md",
        "docs/API-SPEC-limits.yaml",
        "docs/ENGINEERING-HANDBOOK.md",
        "docs/INCIDENT-2041.md",
        "docs/SECURITY-TICKET-317.md",
        "fixtures/incident/repro.py",
        "fixtures/data/customers.csv",
        "deploy/Dockerfile",
        "ui/server.py",
        "ui/index.html",
    ]
    missing = [p for p in expected if not (ROOT / p).exists()]
    assert not missing, f"eksik dosya: {', '.join(missing)}"


def test_git_available():
    """Git kurulu ve klasor bir git deposu"""
    assert shutil.which("git"), "git bulunamadi (https://git-scm.com/downloads)"
    result = run(["git", "rev-parse", "--is-inside-work-tree"])
    assert result.returncode == 0, "bu klasor bir git deposu degil (sablondan olusturdugunuz depoyu klonladiniz mi?)"


def test_semgrep_installed():
    """semgrep kurulu (M5 icin)"""
    executable = _find_semgrep()
    if executable is None and sys.platform == "win32":
        pytest.skip("Windows'ta semgrep yerel kurulamayabilir; M5 taramasini WSL'de calistirin ya da egitmene gosterin")
    assert executable, f"semgrep yok  ->  {SETUP_HINT}"
    result = run([executable, "--version"])
    assert result.returncode == 0, "semgrep bulundu ama calismiyor: " + (result.stderr.strip().splitlines() or ["?"])[-1]


def test_bob_cli_installed():
    """Bob Shell (bob komutu) kurulu (M2 icin)"""
    assert shutil.which("bob"), "'bob' komutu PATH'te yok; kilavuzdaki Bob Shell kurulum adimini izleyin (sonra: bob --version)"
