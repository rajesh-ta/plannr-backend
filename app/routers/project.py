from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectOut)
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
  print("Creating project with data:", data)
  project = Project(**data.model_dump())
  db.add(project)
  await db.commit()
  await db.refresh(project)
  return project

@router.get("/", response_model=list[ProjectOut])
async def get_projects(db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(Project))
  projects = result.scalars().all()
  return projects

@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(Project).where(Project.id == project_id))
  project = result.scalar_one_or_none()
  if not project:
    raise HTTPException(status_code=404, detail="Project not found")
  return project


  