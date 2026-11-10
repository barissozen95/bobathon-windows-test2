"""Shared helpers for the mission checks."""

from __future__ import annotations

import itertools
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_counter = itertools.count(1)


def next_customer_id() -> str:
    """Unique, spec-valid customer id (C + 6 digits) so limits tests need no reset."""
    return f"C{900000 + next(_counter):06d}"


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 120, env: dict | None = None) -> subprocess.CompletedProcess:
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run(
        cmd, cwd=cwd or ROOT, capture_output=True, text=True, timeout=timeout, check=False, env=full_env
    )


def read_text(path: str | Path) -> str:
    p = ROOT / path if not Path(path).is_absolute() else Path(path)
    return p.read_text(encoding="utf-8", errors="replace")


SECRET_VALUES = [
    "ak_live_7f3c9b21d84e4a6f9b0c5d1e2a3b4c5d",
    "Aur0ra!Pay#2024",
    "super-secret-jwt-key-do-not-share",
    "aurora-deploy-token-8f3a91c2d4",
]
SKIP_DIRS = {".git", ".venv", ".venv-tools", "__pycache__", ".verify", "fixtures", ".pytest_cache", "verify"}


def source_files(*suffixes):
    """Repo files minus venvs/fixtures/verify; optionally filtered by suffix or file name."""
    for path in ROOT.rglob("*"):
        if path.is_file() and not (set(path.relative_to(ROOT).parts) & SKIP_DIRS) and (not suffixes or path.suffix in suffixes or path.name in suffixes):
            yield path
