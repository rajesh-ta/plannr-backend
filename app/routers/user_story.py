from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.core.database import get_db
from app.models.user_story import UserStory
from app.schemas.user_story import UserStoryCreate, UserStoryOut

router = APIRouter(prefix="/user-stories", tags=["user-stories"])

@router.post("/", response_model=UserStoryOut)
async def create_user_story(data: UserStoryCreate, db: AsyncSession = Depends(get_db)):
  user_story = UserStory(**data.model_dump())
  db.add(user_story)
  await db.commit()
  await db.refresh(user_story)
  return user_story

@router.get("/", response_model=list[UserStoryOut])
async def get_user_stories(db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(UserStory))
  user_stories = result.scalars().all()
  return user_stories

@router.get("/sprint/{sprint_id}", response_model=list[UserStoryOut])
async def get_user_stories_by_sprint(sprint_id: UUID, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(UserStory).where(UserStory.sprint_id == sprint_id))
  user_stories = result.scalars().all()
  return user_stories

@router.get("/{user_story_id}", response_model=UserStoryOut)
async def get_user_story(user_story_id: UUID, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(UserStory).where(UserStory.id == user_story_id))
  user_story = result.scalar_one_or_none()
  if not user_story:
    raise HTTPException(status_code=404, detail="User story not found")
  return user_story

@router.put("/{user_story_id}", response_model=UserStoryOut)
async def update_user_story(user_story_id: UUID, data: UserStoryCreate, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(UserStory).where(UserStory.id == user_story_id))
  user_story = result.scalar_one_or_none()
  if not user_story:
    raise HTTPException(status_code=404, detail="User story not found")
  
  for key, value in data.model_dump().items():
    setattr(user_story, key, value)
  
  await db.commit()
  await db.refresh(user_story)
  return user_story

@router.delete("/{user_story_id}")
async def delete_user_story(user_story_id: UUID, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(UserStory).where(UserStory.id == user_story_id))
  user_story = result.scalar_one_or_none()
  if not user_story:
    raise HTTPException(status_code=404, detail="User story not found")
  
  await db.delete(user_story)
  await db.commit()
  return {"message": "User story deleted successfully"}
