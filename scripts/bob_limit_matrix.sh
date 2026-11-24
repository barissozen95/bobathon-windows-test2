#!/usr/bin/env bash
# Runs the same small Bob Shell task under different --max-cost / --max-turns
# combinations and stores each JSON result under reports/bob-limits/.
set -uo pipefail

cd "$(dirname "$0")/.."
OUT=reports/bob-limits
mkdir -p "$OUT"

if [[ -z "${BOB_API_KEY:-}" ]]; then
  echo "BOB_API_KEY is not set" >&2
  exit 1
fi

TASK="services/core/fees.py modülünü açıkla: ne yapar, ücret eşiği ve yuvarlama kuralı nedir? En fazla 8 cümle. Hiçbir dosyayı değiştirme."

# name  max-cost  max-turns
COMBOS=(
  "tight   0.05  2"
  "lowcost 0.10  10"
  "lowturn 2     2"
  "balanced 0.50 6"
  "loose   2     15"
)

for combo in "${COMBOS[@]}"; do
  read -r name cost turns <<<"$combo"
  echo ">> $name (max-cost=$cost, max-turns=$turns)"
  start=$(date +%s)
  bob run "$TASK" --format json --mode ask --trust --disable-mcp --accept-license \
    --max-cost "$cost" --max-turns "$turns" --log-level silent \
    >"$OUT/run-$name.json" 2>"$OUT/run-$name.err"
  code=$?
  end=$(date +%s)
  printf '{"name":"%s","max_cost":%s,"max_turns":%s,"exit_code":%s,"wall_seconds":%s}\n' \
    "$name" "$cost" "$turns" "$code" "$((end - start))" >"$OUT/run-$name.meta.json"
  echo "   exit=$code wall=$((end - start))s"
done

# Keep the mission deliverable: the balanced run as reports/bob-run.json
cp "$OUT/run-balanced.json" reports/bob-run.json 2>/dev/null || true
