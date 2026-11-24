"""Reporting helpers: transfer log search and statement archiving."""

import os
import sqlite3
import tarfile

from . import config
from .errors import ValidationFailed

REPORTS_DIR = "reports"

_conn = sqlite3.connect(":memory:", check_same_thread=False)
_conn.execute(
    "CREATE TABLE IF NOT EXISTS transfer_log ("
    "id TEXT, owner_name TEXT, from_account TEXT, to_account TEXT, "
    "amount TEXT, created_at TEXT)"
)

_COLUMNS = ["id", "owner_name", "from_account", "to_account", "amount", "created_at"]
_FIND_BY_OWNER = (
    "SELECT id, owner_name, from_account, to_account, amount, created_at "
    "FROM transfer_log WHERE owner_name = ?"
)


def reset() -> None:
    """Clear the transfer log (called from store.reset())."""
    _conn.execute("DELETE FROM transfer_log")
    _conn.commit()


def record_transfer(transfer: dict, owner_name: str) -> None:
    _conn.execute(
        "INSERT INTO transfer_log VALUES (?, ?, ?, ?, ?, ?)",
        (
            transfer["id"],
            owner_name,
            transfer["from_account"],
            transfer["to_account"],
            str(transfer["amount"]),
            transfer["created_at"],
        ),
    )
    _conn.commit()


def find_transfers_by_owner(owner: str) -> list[dict]:
    # Parameterised query: user input never becomes part of the SQL text (handbook section 5).
    cursor = _conn.execute(_FIND_BY_OWNER, (owner,))
    return [dict(zip(_COLUMNS, row)) for row in cursor.fetchall()]


def archive_statements(filename: str) -> int:
    """Pack the reports directory into <ARCHIVE_DIR>/<filename>.tgz without invoking a shell.

    `filename` is validated by ArchiveRequest (no path separators, no `..`); the resolved
    target is checked again here so a bypass cannot escape ARCHIVE_DIR.
    """
    archive_dir = os.path.realpath(config.ARCHIVE_DIR)
    target = os.path.realpath(os.path.join(archive_dir, f"{filename}.tgz"))
    if os.path.dirname(target) != archive_dir:
        raise ValidationFailed("Geçersiz dosya adı")
    with tarfile.open(target, "w:gz") as tar:
        tar.add(REPORTS_DIR)
    return 0
