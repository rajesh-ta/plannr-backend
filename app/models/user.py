from datetime import datetime
from uuid import uuid4
from typing import Optional
from sqlalchemy import String, TIMESTAMP, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "boards"}

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String(150), unique=True)
    role_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("boards.roles.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    last_modified_on: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_modified_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("boards.users.id", ondelete="SET NULL"),
        nullable=True,
    )
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    google_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(50), default="local")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    # Relationships
    role_info: Mapped[Optional["Role"]] = relationship(  # type: ignore[name-defined]
        "Role", foreign_keys=[role_id], back_populates="users", lazy="select"
    )
    modifier: Mapped[Optional["User"]] = relationship(
        "User", remote_side="User.id", foreign_keys=[last_modified_by], lazy="select"
    )

