from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class UserStoryCreate(BaseModel):
  sprint_id: UUID
  title: str
  description: str | None = None
  status: str
  priority: int | None = None

class UserStoryOut(BaseModel):
  id: UUID
  sprint_id: UUID
  title: str
  description: str | None
  status: str
  priority: int | None
  created_at: datetime

  class Config:
    from_attributes = True
