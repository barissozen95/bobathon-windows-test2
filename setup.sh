#!/usr/bin/env bash
# Aurora Pay - one-time workshop setup.
# Usage: ./setup.sh             python deps only
#        ./setup.sh --scanners  also installs semgrep (Mission 5) in an isolated venv
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
"$PYTHON" - <<'EOF' || { echo "Python 3.10+ gerekli."; exit 1; }
import sys
sys.exit(0 if sys.version_info >= (3, 10) else 1)
EOF

[ -d .venv ] || "$PYTHON" -m venv .venv
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q -r requirements-dev.txt

if [ "${1:-}" = "--scanners" ]; then
  # semgrep pins its own opentelemetry versions; keep it away from the app venv.
  [ -d .venv-tools ] || "$PYTHON" -m venv .venv-tools
  .venv-tools/bin/python -m pip install -q --upgrade pip
  .venv-tools/bin/python -m pip install -q semgrep
fi

echo
echo "Kurulum tamam. Kontrol icin:  ./verify/run.sh m0"
echo "Sanal ortami etkinlestirmek icin:  source .venv/bin/activate"
