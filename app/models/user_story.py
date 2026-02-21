from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Text, func, Identity
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class UserStory(Base):
  __tablename__ = "user_stories"
  __table_args__ = {"schema": "boards"}

  id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
  user_story_no: Mapped[int] = mapped_column(Integer, Identity(start=10000001, cycle=False), unique=True, nullable=False)
  sprint_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("boards.sprints.id"))
  title: Mapped[str] = mapped_column(String(200))
  description: Mapped[str | None] = mapped_column(Text)
  status: Mapped[str] = mapped_column(String(30))
  priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
  created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
  assignee_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("boards.users.id"), nullable=True)