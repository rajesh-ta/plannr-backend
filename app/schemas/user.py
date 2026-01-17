from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
  name: str
  email: str
  role: str

class UserOut(BaseModel):
  id: UUID
  name: str
  email: str
  role: str
  created_at: datetime

  class Config:
    from_attributes = True
