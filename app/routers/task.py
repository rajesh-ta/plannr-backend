from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.core.database import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskOut)
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
  task = Task(**data.model_dump())
  db.add(task)
  await db.commit()
  await db.refresh(task)
  return task

@router.get("/", response_model=list[TaskOut])
async def get_tasks(db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(Task))
  tasks = result.scalars().all()
  return tasks

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(Task).where(Task.id == task_id))
  task = result.scalar_one_or_none()
  if not task:
    raise HTTPException(status_code=404, detail="Task not found")
  return task

@router.put("/{task_id}", response_model=TaskOut)
async def update_task(task_id: UUID, data: TaskCreate, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(Task).where(Task.id == task_id))
  task = result.scalar_one_or_none()
  if not task:
    raise HTTPException(status_code=404, detail="Task not found")
  
  for key, value in data.model_dump().items():
    setattr(task, key, value)
  
  await db.commit()
  await db.refresh(task)
  return task

@router.delete("/{task_id}")
async def delete_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(Task).where(Task.id == task_id))
  task = result.scalar_one_or_none()
  if not task:
    raise HTTPException(status_code=404, detail="Task not found")
  
  await db.delete(task)
  await db.commit()
  return {"message": "Task deleted successfully"}
