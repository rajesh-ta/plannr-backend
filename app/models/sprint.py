from datetime import datetime, date
from uuid import uuid4
from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, Date, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Sprint(Base):
  __tablename__ = "sprints"
  __table_args__ = {"schema": "boards"}

  id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
  name: Mapped[str] = mapped_column(String(150))
  project_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("boards.projects.id"))
  start_date: Mapped[date | None] = mapped_column(Date)
  end_date: Mapped[date | None] = mapped_column(Date)
  status: Mapped[str] = mapped_column(String(50))
  sprint_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
  created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())