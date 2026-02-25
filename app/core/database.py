from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

_raw_database_url = os.getenv("DATABASE_URL", "")

# Render (and many other hosts) provide "postgresql://" URLs.
# SQLAlchemy's asyncpg driver requires "postgresql+asyncpg://".
if _raw_database_url.startswith("postgresql://"):
    DATABASE_URL = _raw_database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _raw_database_url.startswith("postgres://"):
    # Heroku-style shorthand
    DATABASE_URL = _raw_database_url.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = _raw_database_url

class Base(DeclarativeBase):
  pass

# Only require SSL for remote databases (Render, Heroku, etc.).
# Local PostgreSQL instances typically don't support SSL.
_is_remote_db = "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL
_connect_args = {"ssl": "require"} if _is_remote_db else {}

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
  engine, expire_on_commit=False
)

async def get_db():
  async with AsyncSessionLocal() as session:
    yield session
