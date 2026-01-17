from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
  # Check if email already exists
  result = await db.execute(select(User).where(User.email == data.email))
  existing_user = result.scalar_one_or_none()
  if existing_user:
    raise HTTPException(status_code=400, detail="Email already registered")
  
  user = User(
    id=str(uuid4()),
    **data.model_dump(),
    created_at=datetime.now()
  )
  db.add(user)
  await db.commit()
  await db.refresh(user)
  return user

@router.get("/", response_model=list[UserOut])
async def get_users(db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(User))
  users = result.scalars().all()
  return users

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(User).where(User.id == user_id))
  user = result.scalar_one_or_none()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user

@router.put("/{user_id}", response_model=UserOut)
async def update_user(user_id: str, data: UserCreate, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(User).where(User.id == user_id))
  user = result.scalar_one_or_none()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  
  # Check if email is being changed to an existing email
  if data.email != user.email:
    email_check = await db.execute(select(User).where(User.email == data.email))
    if email_check.scalar_one_or_none():
      raise HTTPException(status_code=400, detail="Email already registered")
  
  user.name = data.name
  user.email = data.email
  user.role = data.role
  
  await db.commit()
  await db.refresh(user)
  return user

@router.delete("/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(User).where(User.id == user_id))
  user = result.scalar_one_or_none()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  
  await db.delete(user)
  await db.commit()
  return {"message": "User deleted successfully"}
