# Create routes for sprint CRUD operations
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.sprint import SprintCreate, SprintOut
from app.models.sprint import Sprint

router = APIRouter(
  prefix="/sprints",
  tags=["sprints"],
  dependencies=[Depends(get_current_user)],
)

# create a new sprint
@router.post("/", response_model=SprintOut)
async def create_sprint(data: SprintCreate, db: AsyncSession = Depends(get_db)):
  # Use MAX(sprint_number) + 1 so deletions never cause a unique constraint violation
  result = await db.execute(
    select(func.max(Sprint.sprint_number)).where(Sprint.project_id == data.project_id)
  )
  max_number = result.scalar() or 0
  next_sprint_number = max_number + 1

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