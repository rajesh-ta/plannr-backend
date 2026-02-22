from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import uuid4
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate, UserOut


def _enrich_user(user: User) -> dict:
    """Attach role_name from the loaded relationship (if any)."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role_id": user.role_id,
        "role_name": user.role_info.role_name if user.role_info else None,
        "status": user.status,
        "last_modified_on": user.last_modified_on,
        "last_modified_by": user.last_modified_by,
        "avatar_url": user.avatar_url,
        "auth_provider": user.auth_provider,
        "created_at": user.created_at,
    }


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[UserOut])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).options(selectinload(User.role_info)).order_by(User.name)
    )
    users = result.scalars().all()
    return [_enrich_user(u) for u in users]


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).options(selectinload(User.role_info)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _enrich_user(user)


@router.post("/", response_model=UserOut)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(uuid4()),
        name=data.name,
        email=data.email,
        role_id=str(data.role_id) if data.role_id else None,
        status=data.status,
        created_at=datetime.now(),
        last_modified_on=datetime.now(),
    )
    db.add(user)
    await db.commit()

    result2 = await db.execute(
        select(User).options(selectinload(User.role_info)).where(User.id == user.id)
    )
    user = result2.scalar_one()
    return _enrich_user(user)


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).options(selectinload(User.role_info)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.email and data.email != user.email:
        email_check = await db.execute(select(User).where(User.email == data.email))
        if email_check.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        user.email = data.email

    if data.name is not None:
        user.name = data.name

    if data.role_id is not None:
        role_res = await db.execute(
            select(Role).where(Role.id == str(data.role_id))
        )
        role = role_res.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        user.role_id = str(data.role_id)

    if data.status is not None:
        user.status = data.status

    user.last_modified_on = datetime.now()
    user.last_modified_by = str(current_user.id)

    await db.commit()

    result2 = await db.execute(
        select(User).options(selectinload(User.role_info)).where(User.id == user_id)
    )
    user = result2.scalar_one()
    return _enrich_user(user)


@router.delete("/{user_id}", status_code=200)
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}

