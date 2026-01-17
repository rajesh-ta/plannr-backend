# Create routes for sprint CRUD operations
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List
from app.core.database import get_db
from app.schemas.sprint import SprintCreate, SprintOut
from app.models.sprint import Sprint

router = APIRouter(prefix="/sprints", tags=["sprints"])

# create a new sprint
@router.post("/", response_model=SprintOut)
async def create_sprint(data: SprintCreate, db: AsyncSession = Depends(get_db)):
  # Auto-generate sprint_number by counting existing sprints for this project
  result = await db.execute(
    select(Sprint).where(Sprint.project_id == data.project_id)
  )
  existing_sprints = result.scalars().all()
  next_sprint_number = len(existing_sprints) + 1
  
  sprint = Sprint(**data.model_dump(), sprint_number=next_sprint_number)
  db.add(sprint)
  await db.commit()
  await db.refresh(sprint)
  return sprint

# get all sprints
@router.get("/", response_model=List[SprintOut])
async def get_sprints(db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(Sprint))
  sprints = result.scalars().all()
  return sprints

# get a sprint by id
@router.get("/{sprint_id}", response_model=SprintOut)
async def get_sprint(sprint_id: UUID, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
  sprint = result.scalar_one_or_none()
  if not sprint:
    raise HTTPException(status_code=404, detail="Sprint not found")
  return sprint

# get sprints by project id
@router.get("/project/{project_id}", response_model=List[SprintOut])
async def get_sprints_by_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(Sprint).where(Sprint.project_id == project_id))
  sprints = result.scalars().all()
  return sprints