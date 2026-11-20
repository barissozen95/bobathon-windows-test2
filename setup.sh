#!/usr/bin/env bash
# Aurora Pay - tek seferlik kurulum (macOS ve Linux). Asıl iş setup.py içinde; bu betik onu çağırır.
# Kullanım:  ./setup.sh --scanners
# Başka bir Python ile:  PYTHON=/yol/python3.12 ./setup.sh --scanners
set -euo pipefail
cd "$(dirname "$0")"
exec "${PYTHON:-python3}" setup.py "$@"
