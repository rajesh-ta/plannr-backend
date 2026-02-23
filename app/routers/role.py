from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import uuid4

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.permission import Permission
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut, RolePermissionOut, RolePermissionUpdate

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
)


@router.get("/", response_model=list[RoleOut])
async def get_roles(db: AsyncSession = Depends(get_db)):
    """Public — returns all active roles (used on signup page)."""
    result = await db.execute(select(Role).order_by(Role.role_name))
    roles = result.scalars().all()
    return roles


@router.get("/{role_id}", response_model=RoleOut, dependencies=[Depends(get_current_user)])
async def get_role(role_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/", response_model=RoleOut, status_code=201, dependencies=[Depends(get_current_user)])
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


@router.put("/{role_id}", response_model=RoleOut, dependencies=[Depends(get_current_user)])
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


@router.delete("/{role_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_role(role_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    await db.delete(role)
    await db.commit()


# ─── Role permission endpoints ────────────────────────────────────────────────

@router.get(
    "/{role_id}/permissions",
    response_model=list[RolePermissionOut],
    dependencies=[Depends(get_current_user)],
)
async def get_role_permissions(role_id: str, db: AsyncSession = Depends(get_db)):
    """Return all 12 permissions for a role with their is_granted flag."""
    result = await db.execute(
        select(RolePermission)
        .where(RolePermission.role_id == role_id)
        .options(selectinload(RolePermission.permission))
        .order_by(RolePermission.permission_id)
    )
    rps = result.scalars().all()
    if not rps:
        raise HTTPException(status_code=404, detail="Role not found or has no permissions")
    return [
        RolePermissionOut(
            role_permission_id=rp.id,
            permission_id=rp.permission_id,
            permission_name=rp.permission.name,
            is_granted=rp.is_granted,
        )
        for rp in rps
    ]


@router.patch(
    "/{role_id}/permissions/{permission_id}",
    response_model=RolePermissionOut,
    dependencies=[Depends(get_current_user)],
)
async def update_role_permission(
    role_id: str,
    permission_id: str,
    data: RolePermissionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Toggle is_granted for a specific role-permission pair."""
    result = await db.execute(
        select(RolePermission)
        .where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
        .options(selectinload(RolePermission.permission))
    )
    rp = result.scalar_one_or_none()
    if not rp:
        raise HTTPException(status_code=404, detail="Role-permission pair not found")

    rp.is_granted = data.is_granted
    await db.commit()
    await db.refresh(rp)

    return RolePermissionOut(
        role_permission_id=rp.id,
        permission_id=rp.permission_id,
        permission_name=rp.permission.name,
        is_granted=rp.is_granted,
    )
