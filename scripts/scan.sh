#!/usr/bin/env bash
# Semgrep ile guvenlik taramasi (M5). Asıl iş scan.py içinde (Windows, macOS, Linux ortak).
# Kullanim:  ./scripts/scan.sh            (ozet)
#            ./scripts/scan.sh --verbose  (her bulgu)
cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python
[ -x "$PY" ] || PY=python3
exec "$PY" scripts/scan.py "$@"
