#!/usr/bin/env bash
# Aurora Pay - gorev dogrulayici. Kullanim: ./verify/run.sh [m0..m8|all]
cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python
[ -x "$PY" ] || PY=python3
exec "$PY" verify/run.py "$@"
