#!/usr/bin/env python3
"""Semgrep ile güvenlik taraması (M5). Çıkış kodu: 0 = temiz, 1 = bulgu var, 2 = Semgrep çalışmadı.

Kullanım (repo kökünden):
    python3 scripts/scan.py              özet (Windows: py scripts/scan.py)
    python3 scripts/scan.py --verbose    her bulgu
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def find_semgrep():
    for folder in (".venv-tools/bin", ".venv-tools/Scripts", ".venv/bin", ".venv/Scripts"):
        for exe in ("semgrep", "semgrep.exe"):
            candidate = ROOT / folder / exe
            if candidate.exists():
                return str(candidate)
    return shutil.which("semgrep")


def main(argv):
    semgrep = find_semgrep()
    if not semgrep:
        print("semgrep bulunamadi.  ->  python3 setup.py --scanners  (Windows: py setup.py --scanners)")
        return 2

    result = subprocess.run(
        [
            semgrep,
            "--config", "security/semgrep-rules.yml",
            "--metrics=off", "--disable-version-check", "--quiet", "--json",
            "services", "deploy",
        ],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0 and not result.stdout.strip():
        print("semgrep calistirilamadi (cikis kodu %d)" % result.returncode)
        return 2

    results = json.loads(result.stdout).get("results", [])
    by_rule = {}
    for item in results:
        by_rule.setdefault(item["check_id"].split(".")[-1], []).append(item)
    if "--verbose" in argv:
        for item in results:
            print("%s:%s  %s" % (item["path"], item["start"]["line"], item["check_id"].split(".")[-1]))
    print("Semgrep bulgu sayisi: %d" % len(results))
    for rule, items in sorted(by_rule.items()):
        print("  %2d  %s" % (len(items), rule))
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
