from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime

class SprintCreate(BaseModel):
  name: str
  project_id: UUID
  start_date: date | None = None
  end_date: date | None = None
  status: str

class SprintOut(BaseModel):
  id: UUID
  name: str
  project_id: UUID
  start_date: date | None = None
  end_date: date | None = None
  status: str
  sprint_number: int
  created_at: datetime

  class Config:
    from_attributes = True