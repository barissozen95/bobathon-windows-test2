"""Aurora Core configuration.

Secrets are never stored in the repo (ENGINEERING-HANDBOOK section 5); they are read from
environment variables at import time.
"""

import os

API_KEY = os.environ.get("AURORA_API_KEY", "")
DB_PASSWORD = os.environ.get("AURORA_DB_PASSWORD", "")
JWT_SECRET = os.environ.get("AURORA_JWT_SECRET", "")

DB_URL = os.environ.get("AURORA_DB_URL", "")

ARCHIVE_DIR = os.environ.get("AURORA_ARCHIVE_DIR", "archives")
