from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[RoleOut])
async def get_roles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Role).order_by(Role.role_name))
    roles = result.scalars().all()
    return roles


@router.get("/{role_id}", response_model=RoleOut)
async def get_role(role_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/", response_model=RoleOut, status_code=201)
async def create_role(data: RoleCreate, db: AsyncSession = Depends(get_db)):
    # Prevent duplicate role names
    existing = await db.execute(
        select(Role).where(Role.role_name == data.role_name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Role name already exists")

    role = Role(id=str(uuid4()), **data.model_dump())
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@router.put("/{role_id}", response_model=RoleOut)
async def update_role(
    role_id: str, data: RoleUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(role, field, value)

    await db.commit()
    await db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    await db.delete(role)
    await db.commit()
