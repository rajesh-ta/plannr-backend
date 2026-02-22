import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-super-secret-key-32chars")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
