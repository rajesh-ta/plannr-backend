import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-super-secret-key-32chars")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")

# Comma-separated list of allowed CORS origins.
# Defaults cover the two common local dev addresses.
_raw_origins = os.getenv(
    "CORS_ORIGINS",
    "*",
    "http://localhost:3000,http://127.0.0.1:3000",
)
CORS_ORIGINS: list[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]
