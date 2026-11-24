"""SQLite-backed transfer log used for owner reports."""

import sqlite3

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
    _conn.execute("DELETE FROM transfer_log")
    _conn.commit()


def record(transfer: dict, owner_name: str) -> None:
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


def find_by_owner(owner: str) -> list[dict]:
    # Parameterised query: user input never becomes part of the SQL text (handbook section 5).
    cursor = _conn.execute(_FIND_BY_OWNER, (owner,))
    return [dict(zip(_COLUMNS, row)) for row in cursor.fetchall()]
