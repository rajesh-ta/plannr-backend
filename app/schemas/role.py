from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class RoleCreate(BaseModel):
    role_name: str
    description: Optional[str] = None
    is_active: bool = True


class RoleUpdate(BaseModel):
    role_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoleOut(BaseModel):
    id: UUID
    role_name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    modified_at: datetime

    class Config:
        from_attributes = True


class RolePermissionOut(BaseModel):
    role_permission_id: UUID
    permission_id: UUID
    permission_name: str
    is_granted: bool

    class Config:
        from_attributes = True


class RolePermissionUpdate(BaseModel):
    is_granted: bool
