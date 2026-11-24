"""API tests for Aurora Core reports: GET /reports/transfers and POST /reports/archive."""

import tarfile

import pytest
from fastapi.testclient import TestClient

from services.core import store
from services.core.main import app
from tests.helpers import assert_error

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_store():
    store.reset()


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    """Isolated cwd with reports/ and archives/ so nothing is written inside the repo."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "statement.txt").write_text("ekstre")
    (tmp_path / "archives").mkdir()
    return tmp_path


def _setup_transfer(owner="Ayse Demir"):
    client.post("/accounts", json={"id": "A", "owner_name": owner, "iban": "TR00A", "balance": "1000.00"})
    client.post("/accounts", json={"id": "B", "owner_name": "Mehmet Arslan", "iban": "TR00B", "balance": "0.00"})
    resp = client.post("/transfers", json={"from_account": "A", "to_account": "B", "amount": "10.00"})
    assert resp.status_code == 201
    return resp.json()


# --- GET /reports/transfers -----------------------------------------------


def test_report_returns_transfer_for_owner():
    # Arrange
    transfer = _setup_transfer()
    # Act
    resp = client.get("/reports/transfers", params={"owner": "Ayse Demir"})
    # Assert
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 1
    assert rows[0]["id"] == transfer["id"]
    assert rows[0]["from_account"] == "A"


def test_report_is_empty_after_store_reset():
    # Arrange
    _setup_transfer()
    store.reset()
    # Act
    resp = client.get("/reports/transfers", params={"owner": "Ayse Demir"})
    # Assert
    assert resp.status_code == 200
    assert resp.json() == []


def test_report_rejects_missing_owner():
    # Act
    resp = client.get("/reports/transfers")
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")


def test_report_sql_injection_returns_empty_list():
    # Arrange
    _setup_transfer()
    # Act
    resp = client.get("/reports/transfers", params={"owner": "x' OR '1'='1"})
    # Assert
    assert resp.status_code == 200
    assert resp.json() == []


def test_report_owner_with_apostrophe_returns_empty_list():
    # Arrange
    _setup_transfer()
    # Act
    resp = client.get("/reports/transfers", params={"owner": "O'Brien"})
    # Assert
    assert resp.status_code == 200
    assert resp.json() == []


def test_report_owner_with_apostrophe_finds_own_transfer():
    # Arrange
    transfer = _setup_transfer(owner="O'Brien")
    # Act
    resp = client.get("/reports/transfers", params={"owner": "O'Brien"})
    # Assert
    assert resp.status_code == 200
    assert [row["id"] for row in resp.json()] == [transfer["id"]]


def test_report_owner_empty_string_returns_empty_list():
    # Arrange
    _setup_transfer()
    # Act
    resp = client.get("/reports/transfers", params={"owner": ""})
    # Assert
    assert resp.status_code == 200
    assert resp.json() == []


# --- POST /reports/archive ------------------------------------------------


def test_archive_creates_tgz_with_reports(workdir):
    # Act
    resp = client.post("/reports/archive", json={"filename": "march-2025"})
    # Assert
    assert resp.status_code == 200
    assert resp.json() == {"exit_code": 0}
    target = workdir / "archives" / "march-2025.tgz"
    assert target.exists()
    with tarfile.open(target, "r:gz") as tar:
        names = tar.getnames()
    assert "reports/statement.txt" in names


def test_archive_rejects_missing_body(workdir):
    # Act
    resp = client.post("/reports/archive")
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")


def test_archive_rejects_missing_filename(workdir):
    # Act
    resp = client.post("/reports/archive", json={})
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")


@pytest.mark.parametrize("filename", ["../x", "a..b", "..", "/etc/passwd", "sub/dir", ".hidden", ""])
def test_archive_rejects_path_traversal(workdir, filename):
    # Act
    resp = client.post("/reports/archive", json={"filename": filename})
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert list((workdir / "archives").iterdir()) == []
    assert not (workdir / "x.tgz").exists()


@pytest.mark.parametrize("filename", ["x; touch PWNED", "$(touch PWNED)", "`touch PWNED`", "a|touch PWNED",
                                      "a && touch PWNED", "a b"])
def test_archive_rejects_shell_metacharacters(workdir, filename):
    # Act
    resp = client.post("/reports/archive", json={"filename": filename})
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert not (workdir / "PWNED").exists()
    assert not (workdir / "archives" / "PWNED").exists()
    assert list((workdir / "archives").iterdir()) == []


def test_archive_accepts_filename_of_100_chars(workdir):
    # Arrange
    filename = "a" * 100
    # Act
    resp = client.post("/reports/archive", json={"filename": filename})
    # Assert
    assert resp.status_code == 200
    assert (workdir / "archives" / f"{filename}.tgz").exists()


def test_archive_rejects_filename_of_101_chars(workdir):
    # Act
    resp = client.post("/reports/archive", json={"filename": "a" * 101})
    # Assert
    assert_error(resp, 422, "VALIDATION_ERROR")
    assert list((workdir / "archives").iterdir()) == []


def test_archive_accepts_single_char_filename(workdir):
    # Act
    resp = client.post("/reports/archive", json={"filename": "a"})
    # Assert
    assert resp.status_code == 200
    assert (workdir / "archives" / "a.tgz").exists()
