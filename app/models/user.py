from datetime import datetime
from sqlalchemy import String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
  __tablename__ = "users"
  __table_args__ = {"schema": "boards"}

  id: Mapped[str] = mapped_column(UUID, primary_key=True)
  name: Mapped[str] = mapped_column(String)
  email: Mapped[str] = mapped_column(String(150), unique=True)
  role: Mapped[str] = mapped_column(String(50))
  created_at: Mapped[datetime] = mapped_column(TIMESTAMP)
