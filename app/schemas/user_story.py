from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class UserStoryCreate(BaseModel):
  sprint_id: UUID
  title: str
  description: str | None = None
  status: str
  priority: int | None = None
  assignee_id: UUID | None = None

class UserStoryOut(BaseModel):
  id: UUID
  user_story_no: int
  sprint_id: UUID
  title: str
  description: str | None
  status: str
  priority: int | None
  created_at: datetime
  assignee_id: UUID | None

  class Config:
    from_attributes = True
