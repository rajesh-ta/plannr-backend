import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-super-secret-key-32chars")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")

# Comma-separated list of allowed CORS origins.
# Set the CORS_ORIGINS env var in production (e.g. "https://yourapp.com").
# Defaults to "*" (allow all) when the env var is not set.
_raw_origins = os.getenv("CORS_ORIGINS", "*")
CORS_ORIGINS: list[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]
