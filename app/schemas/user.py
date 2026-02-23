from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: str
    role_id: Optional[UUID] = None
    status: str = "ACTIVE"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[UUID] = None
    status: Optional[str] = None


class UserOut(BaseModel):
    id: UUID
    name: str
    email: str
    role_id: Optional[UUID] = None
    role_name: Optional[str] = None          # resolved from role_info relationship
    status: str = "ACTIVE"
    last_modified_on: Optional[datetime] = None
    last_modified_by: Optional[UUID] = None
    avatar_url: Optional[str] = None
    auth_provider: str = "local"
    created_at: datetime
    # RBAC: all 12 permission keys always present; True = granted by the user's role
    permissions: dict[str, bool] = {}

    class Config:
        from_attributes = True

