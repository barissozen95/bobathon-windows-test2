#!/usr/bin/env bash
# Semgrep ile guvenlik taramasi (Mission 5). Cikis kodu: 0 = temiz, 1 = bulgu var.
# Kullanim:  ./scripts/scan.sh            (ozet)
#            ./scripts/scan.sh --verbose  (her bulgu)
cd "$(dirname "$0")/.." || exit 1

SEMGREP=""
for candidate in .venv-tools/bin/semgrep .venv/bin/semgrep "$(command -v semgrep || true)"; do
  if [ -n "$candidate" ] && [ -x "$candidate" ]; then SEMGREP="$candidate"; break; fi
done
if [ -z "$SEMGREP" ]; then
  echo "semgrep bulunamadi.  ->  ./setup.sh --scanners"
  exit 2
fi

OUT=$(mktemp)
"$SEMGREP" --config security/semgrep-rules.yml --metrics=off --disable-version-check --quiet --json \
  services deploy > "$OUT" 2>/dev/null
STATUS=$?
if [ $STATUS -ne 0 ] && [ ! -s "$OUT" ]; then
  echo "semgrep calistirilamadi (cikis kodu $STATUS)"
  exit 2
fi

PY=.venv/bin/python
[ -x "$PY" ] || PY=python3
"$PY" - "$OUT" "${1:-}" <<'EOF'
import json, sys
data = json.load(open(sys.argv[1]))
results = data.get("results", [])
verbose = sys.argv[2] == "--verbose"
by_rule = {}
for r in results:
    by_rule.setdefault(r["check_id"].split(".")[-1], []).append(r)
if verbose:
    for r in results:
        print(f'{r["path"]}:{r["start"]["line"]}  {r["check_id"].split(".")[-1]}')
print(f"Semgrep bulgu sayisi: {len(results)}")
for rule, items in sorted(by_rule.items()):
    print(f"  {len(items):>2}  {rule}")
sys.exit(1 if results else 0)
EOF
CODE=$?
rm -f "$OUT"
exit $CODE
