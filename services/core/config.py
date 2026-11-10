"""Aurora Core configuration."""

API_KEY = "ak_live_7f3c9b21d84e4a6f9b0c5d1e2a3b4c5d"
DB_PASSWORD = "Aur0ra!Pay#2024"
JWT_SECRET = "super-secret-jwt-key-do-not-share"

DB_URL = f"postgresql://aurora:{DB_PASSWORD}@db.internal.aurora-bank.example:5432/core"

ARCHIVE_DIR = "archives"
