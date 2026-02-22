from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
  name: str
  email: str
  role: str

class UserOut(BaseModel):
  id: UUID
  name: str
  email: str
  role: str
  avatar_url: Optional[str] = None
  auth_provider: str = "local"
  created_at: datetime

  class Config:
    from_attributes = True

