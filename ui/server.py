#!/usr/bin/env python3
"""Aurora Pay arayüzü: tek komutla servisleri ve tarayıcı arayüzünü başlatır.

Kullanım (repo kökünden):
    python3 ui/server.py        macOS ve Linux
    py ui/server.py             Windows
Sonra tarayıcıda açın:  http://127.0.0.1:8080

Ne yapar?
  - Aurora Core servisini 8000 portunda başlatır.
  - services/limits/main.py varsa (M1'den sonra) Limits servisini 8001 portunda başlatır.
    Dosya sonradan oluşturulursa kendiliğinden başlatılır.
  - Servisler --reload ile çalışır: Bob kodu değiştirince servis kendini yeniler,
    sayfada hemen sonucu görürsünüz (bellekteki veriler yenilemede sıfırlanır).
  - Tarayıcı sayfasını sunar ve istekleri servislere iletir (CORS sorunu çıkmaz).

Yalnızca Python standart kütüphanesini kullanır. Durdurmak için Ctrl+C.
"""

import http.client
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI_FILE = Path(__file__).resolve().parent / "index.html"
UI_PORT = 8080
HOST = "127.0.0.1"
IS_WINDOWS = os.name == "nt"

SERVICES = {
    "core": {"target": "services.core.main:app", "port": 8000, "entry": "services/core/main.py"},
    "limits": {"target": "services.limits.main:app", "port": 8001, "entry": "services/limits/main.py"},
}
PROCS = {}


def venv_python():
    candidate = ROOT / ".venv" / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")
    return str(candidate) if candidate.exists() else sys.executable


def port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        return sock.connect_ex((HOST, port)) == 0


def start_service(name):
    cfg = SERVICES[name]
    print("[ui] %s servisi başlatılıyor (port %d)" % (name, cfg["port"]), flush=True)
    PROCS[name] = subprocess.Popen(
        [
            venv_python(), "-m", "uvicorn", cfg["target"],
            "--host", HOST, "--port", str(cfg["port"]),
            "--reload", "--reload-dir", "services",
        ],
        cwd=str(ROOT),
    )


def stop_service(proc):
    if proc.poll() is not None:
        return
    if IS_WINDOWS:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
    else:
        proc.terminate()


def supervise():
    """Servisleri ayakta tutar; M1'de services/limits/main.py sonradan oluşunca onu da başlatır."""
    while True:
        for name, cfg in SERVICES.items():
            proc = PROCS.get(name)
            running = proc is not None and proc.poll() is None
            if running or port_open(cfg["port"]):
                continue
            if not (ROOT / cfg["entry"]).exists():
                continue
            if proc is not None:
                time.sleep(3)  # çöktüyse (ör. söz dizimi hatası) hemen tekrar denemeyin
            start_service(name)
        time.sleep(2)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # sessiz
        pass

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status, text):
        self._send(status, text.encode("utf-8"), "application/json; charset=utf-8")

    def _proxy(self):
        parts = self.path.split("/", 3)  # ['', 'api', '<servis>', '<yol>']
        name = parts[2] if len(parts) > 2 else ""
        if name not in SERVICES:
            return self._json(404, '{"proxy_error": "bilinmeyen servis"}')
        rest = "/" + (parts[3] if len(parts) > 3 else "")
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        headers = {}
        for key in ("Content-Type", "Idempotency-Key"):
            if self.headers.get(key):
                headers[key] = self.headers[key]
        try:
            conn = http.client.HTTPConnection(HOST, SERVICES[name]["port"], timeout=15)
            conn.request(self.command, rest, body=body, headers=headers)
            resp = conn.getresponse()
            data = resp.read()
            self._send(resp.status, data, resp.getheader("Content-Type") or "text/plain")
            conn.close()
        except OSError:
            self._json(502, '{"proxy_error": "%s servisi çalışmıyor"}' % name)

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html"):
            return self._send(200, UI_FILE.read_bytes(), "text/html; charset=utf-8")
        if self.path == "/api/status":
            state = ",".join('"%s": %s' % (n, "true" if port_open(c["port"]) else "false") for n, c in SERVICES.items())
            return self._json(200, "{%s}" % state)
        if self.path.startswith("/api/"):
            return self._proxy()
        self._json(404, '{"proxy_error": "bulunamadı"}')

    do_POST = do_PUT = do_DELETE = lambda self: self._proxy() if self.path.startswith("/api/") else self._json(404, "{}")  # noqa: E731


def main():
    if port_open(UI_PORT):
        print("Port %d dolu: arayüz zaten çalışıyor olabilir. http://%s:%d adresini açın." % (UI_PORT, HOST, UI_PORT))
        return 1
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    threading.Thread(target=supervise, daemon=True).start()
    server = ThreadingHTTPServer((HOST, UI_PORT), Handler)
    print("Aurora Pay arayüzü: http://%s:%d   (durdurmak için Ctrl+C)" % (HOST, UI_PORT), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        for proc in PROCS.values():
            stop_service(proc)
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
