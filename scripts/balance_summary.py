"""Build an aggregate balance summary from the customer CSV without exposing PII.

Only the ``balance_try`` column is read; no other field is printed or written.
Usage: python scripts/balance_summary.py [csv_path] [output_path]
"""

import csv
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

CENT = Decimal("0.01")
DEFAULT_CSV = Path("fixtures/data/customers.csv")
DEFAULT_OUT = Path("reports/balance-summary.md")


def money(value: Decimal) -> str:
    return f"{value.quantize(CENT, rounding=ROUND_HALF_UP):,.2f}"


def main() -> int:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT

    balances: list[Decimal] = []
    skipped = 0
    with csv_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                balances.append(Decimal(row["balance_try"].strip()))
            except (InvalidOperation, AttributeError, KeyError):
                skipped += 1

    if not balances:
        print("No valid balances found.", file=sys.stderr)
        return 1

    total = sum(balances, Decimal("0"))
    lines = [
        "# Bakiye Özeti",
        "",
        f"Kaynak: `{csv_path.as_posix()}` (yalnızca `balance_try` sütunu okunmuştur; kişisel veri içermez)",
        "",
        "| Metrik | Değer |",
        "|---|---|",
        f"| Müşteri sayısı | {len(balances)} |",
        f"| Toplam bakiye (TRY) | {money(total)} |",
        f"| Ortalama bakiye (TRY) | {money(total / len(balances))} |",
        f"| En yüksek bakiye (TRY) | {money(max(balances))} |",
        f"| En düşük bakiye (TRY) | {money(min(balances))} |",
        "",
        "Hesaplama `decimal.Decimal` ile, yuvarlama `ROUND_HALF_UP` (2 ondalık).",
    ]
    if skipped:
        lines.append(f"\nGeçersiz bakiye nedeniyle atlanan satır: {skipped}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} ({len(balances)} customers, {skipped} skipped)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
