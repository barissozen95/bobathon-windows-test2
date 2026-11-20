#!/usr/bin/env python3
"""Aurora Pay Bobathon: tek seferlik kurulum (Windows, macOS ve Linux).

Kullanım (repo kökünden):
    python3 setup.py --scanners      macOS ve Linux
    py setup.py --scanners           Windows

Ne yapar?
  1. Gereksinimleri kontrol eder (Python 3.11+, venv, pip, git, bob).
  2. .venv klasörüne uygulama ve test bağımlılıklarını kurar.
  3. --scanners verilirse .venv-tools klasörüne Semgrep'i kurar (M5 için).

Bu betik yalnızca Python standart kütüphanesini kullanır.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent
MIN_PYTHON = (3, 11)
IS_WINDOWS = os.name == "nt"
PY_CMD = "py" if IS_WINDOWS else "python3"


def venv_python(name):
    sub = "Scripts/python.exe" if IS_WINDOWS else "bin/python"
    return ROOT / name / sub


def say(text=""):
    print(text, flush=True)


def fail(text):
    say("")
    say("HATA: " + text)
    sys.exit(1)


def check_python():
    found = "%d.%d" % sys.version_info[:2]
    if sys.version_info[:2] < MIN_PYTHON:
        example = (
            "C:\\yol\\python.exe setup.py --scanners" if IS_WINDOWS else "PYTHON=/yol/python3.12 ./setup.sh --scanners"
        )
        fail(
            "Python %d.%d veya üzeri gerekli, bulunan: %s.\n"
            "Daha yeni bir Python kurun (https://www.python.org/downloads/) ve komutu o Python ile çalıştırın.\n"
            "Örnek: %s" % (MIN_PYTHON[0], MIN_PYTHON[1], found, example)
        )
    say("[tamam] Python %s" % found)


def check_venv_module():
    try:
        import ensurepip  # noqa: F401
        import venv  # noqa: F401
    except ImportError:
        fail(
            "Python'un 'venv' veya 'pip' bileşeni eksik.\n"
            "Debian/Ubuntu: sudo apt install python3-venv python3-pip\n"
            "Yönetici yetkiniz yoksa: eğitmenden hazır ortam isteyin ya da 'uv' ile sanal ortam kurun (https://docs.astral.sh/uv/)."
        )
    say("[tamam] venv ve pip bileşenleri")


def check_tools():
    warnings = []
    if shutil.which("git"):
        say("[tamam] git")
    else:
        warnings.append("git bulunamadı. Kurun: https://git-scm.com/downloads")
    if shutil.which("bob"):
        say("[tamam] Bob Shell (bob komutu)")
    else:
        hint = "Bob Shell bulunamadı (M2 için gerekli). Kılavuzdaki Bob Shell kurulum adımına bakın."
        if not shutil.which("npm"):
            hint += " Önce Node.js ve npm kurulmalı: https://nodejs.org/"
        warnings.append(hint)
    if os.environ.get("BOB_API_KEY"):
        say("[tamam] BOB_API_KEY tanımlı")
    else:
        warnings.append("BOB_API_KEY tanımlı değil (M2 ve M7'deki 'bob run' komutları için gerekli). Kılavuzdaki ön hazırlık bölümüne bakın.")
    if not shutil.which("gh"):
        warnings.append("GitHub CLI (gh) bulunamadı. M8'de PR ve CI kontrolü için önerilir: https://cli.github.com/")
    return warnings


def run(cmd, what):
    result = subprocess.run([str(c) for c in cmd], cwd=str(ROOT))
    if result.returncode != 0:
        fail("%s adımı başarısız oldu. Yukarıdaki pip çıktısına bakın." % what)


def make_venv(name):
    target = ROOT / name
    if not venv_python(name).exists():
        say("%s oluşturuluyor..." % name)
        run([sys.executable, "-m", "venv", target], "Sanal ortam (%s)" % name)
    return venv_python(name)


def main():
    scanners = "--scanners" in sys.argv[1:]
    unknown = [a for a in sys.argv[1:] if a != "--scanners"]
    if unknown:
        fail("Bilinmeyen seçenek: %s\nKullanım: %s setup.py [--scanners]" % (" ".join(unknown), PY_CMD))

    say("Aurora Pay kurulumu: önce gereksinimler kontrol ediliyor")
    check_python()
    check_venv_module()
    warnings = check_tools()

    say("")
    say("Bağımlılıklar kuruluyor (birkaç dakika sürebilir)")
    app_python = make_venv(".venv")
    run([app_python, "-m", "pip", "install", "-q", "--upgrade", "pip"], "pip güncelleme")
    run([app_python, "-m", "pip", "install", "-q", "-r", "requirements-dev.txt"], "Bağımlılık kurulumu")
    say("[tamam] Uygulama ve test bağımlılıkları (.venv)")

    if scanners:
        # Semgrep kendi opentelemetry sürümlerini sabitler; uygulama ortamından ayrı tutulur.
        tools_python = make_venv(".venv-tools")
        run([tools_python, "-m", "pip", "install", "-q", "--upgrade", "pip"], "pip güncelleme (.venv-tools)")
        result = subprocess.run([str(tools_python), "-m", "pip", "install", "-q", "semgrep"], cwd=str(ROOT))
        if result.returncode == 0:
            say("[tamam] Semgrep (.venv-tools)")
        elif IS_WINDOWS:
            warnings.append(
                "Semgrep Windows'ta yerel olarak kurulamadı. M5'te taramayı WSL içinde çalıştırın "
                "ya da eğitmene gösterin. GitHub'daki CI taramasını zaten yapar."
            )
        else:
            fail("Semgrep kurulumu başarısız oldu. Yukarıdaki pip çıktısına bakın.")

    say("")
    if warnings:
        say("Eksikler (şimdi zorunlu değil, ilgili görevden önce tamamlayın):")
        for item in warnings:
            say("  - " + item)
        say("")
    say("Kurulum tamam. Şimdi doğrulayın:")
    say("  %s verify/run.py m0" % PY_CMD)
    say("(Sanal ortamı elle etkinleştirmeniz gerekmez.)")


if __name__ == "__main__":
    main()
