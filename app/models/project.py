from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Project(Base):
  __tablename__ = "projects"
  __table_args__ = {"schema": "boards"}

  id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
  name: Mapped[str] = mapped_column(String(150))
  description: Mapped[str | None] = mapped_column(Text)
  created_by: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("boards.users.id"))
  created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())