from datetime import datetime
from uuid import uuid4
from typing import Optional
from sqlalchemy import String, TIMESTAMP, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
  __tablename__ = "users"
  __table_args__ = {"schema": "boards"}

  id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
  name: Mapped[str] = mapped_column(String)
  email: Mapped[str] = mapped_column(String(150), unique=True)
  role: Mapped[str] = mapped_column(String(50))
  password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
  google_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
  avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  auth_provider: Mapped[str] = mapped_column(String(50), default="local")
  created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

