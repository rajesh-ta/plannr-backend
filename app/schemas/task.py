from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TaskCreate(BaseModel):
  user_story_id: UUID
  title: str
  description: str | None = None
  status: str
  estimated_hours: int | None = None
  assignee_id: UUID | None = None

class TaskOut(BaseModel):
  id: UUID
  user_story_id: UUID
  title: str
  description: str | None
  status: str
  estimated_hours: int | None
  created_at: datetime
  assignee_id: UUID | None

  class Config:
    from_attributes = True
