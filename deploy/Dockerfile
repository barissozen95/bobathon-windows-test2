FROM python:3.12-slim

# Secrets (e.g. GITHUB_TOKEN) are never baked into the image; inject them at
# runtime via the orchestrator's secret store / environment variables.

# Vendor archive is fetched explicitly over HTTPS and verified against a pinned
# SHA-256 (passed at build time) instead of `ADD <url>`, which has no integrity check.
ARG LIBFX_URL=https://artifacts.aurora-bank.example/vendor/libfx-1.4.tar.gz
ARG LIBFX_SHA256
RUN test -n "$LIBFX_SHA256" || { echo "LIBFX_SHA256 build arg is required" >&2; exit 1; } \
    && python -c "import urllib.request, sys; urllib.request.urlretrieve(sys.argv[1], sys.argv[2])" "$LIBFX_URL" /tmp/libfx.tar.gz \
    && echo "$LIBFX_SHA256  /tmp/libfx.tar.gz" | sha256sum -c -

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=app:app . .

USER app

CMD ["uvicorn", "services.core.main:app", "--host", "0.0.0.0", "--port", "8000"]
