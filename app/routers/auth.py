from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import uuid4
import httpx

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from app.core.config import GOOGLE_CLIENT_ID
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, GoogleAuthRequest, AuthResponse
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_to_out(user: User) -> UserOut:
    """Build a UserOut from an ORM User with role_info eagerly loaded."""
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role_id=user.role_id,
        role_name=user.role_info.role_name if user.role_info else None,
        status=user.status,
        last_modified_on=user.last_modified_on,
        last_modified_by=user.last_modified_by,
        avatar_url=user.avatar_url,
        auth_provider=user.auth_provider,
        created_at=user.created_at,
    )


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user with email and password."""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(uuid4()),
        name=data.name,
        email=data.email,
        password_hash=get_password_hash(data.password),
        auth_provider="local",
    )
    db.add(user)
    await db.commit()

    result2 = await db.execute(
        select(User).options(selectinload(User.role_info)).where(User.id == user.id)
    )
    user = result2.scalar_one()
    token = create_access_token({"sub": str(user.id)})
    return AuthResponse(access_token=token, user=_user_to_out(user))


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    result2 = await db.execute(
        select(User).options(selectinload(User.role_info)).where(User.id == user.id)
    )
    user = result2.scalar_one()
    token = create_access_token({"sub": str(user.id)})
    return AuthResponse(access_token=token, user=_user_to_out(user))


@router.post("/google", response_model=AuthResponse)
async def google_auth(data: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Verify a Google ID token from the frontend (@react-oauth/google) and
    sign in or create the user automatically.
    """
    # Verify the Google ID token via Google's tokeninfo endpoint
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": data.credential},
            timeout=10.0,
        )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    google_data = response.json()

    # Validate that the token was issued for our app
    if GOOGLE_CLIENT_ID and google_data.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Google token audience mismatch")

    google_id: str = google_data.get("sub")
    email: str = google_data.get("email", "")
    name: str = google_data.get("name", email.split("@")[0])
    avatar_url: str = google_data.get("picture", "")

    if not google_id or not email:
        raise HTTPException(status_code=400, detail="Incomplete Google profile data")

    # Try to find by google_id first, then by email
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    if not user:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            # Link Google account to existing email user
            user.google_id = google_id
            user.avatar_url = avatar_url or user.avatar_url
            user.auth_provider = "google"
        else:
            # Create brand-new user
            user = User(
                id=str(uuid4()),
                name=name,
                email=email,
                google_id=google_id,
                avatar_url=avatar_url,
                auth_provider="google",
            )
            db.add(user)

    await db.commit()

    result2 = await db.execute(
        select(User).options(selectinload(User.role_info)).where(User.id == user.id)
    )
    user = result2.scalar_one()
    token = create_access_token({"sub": str(user.id)})
    return AuthResponse(access_token=token, user=_user_to_out(user))


@router.get("/me", response_model=UserOut)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the currently authenticated user."""
    result = await db.execute(
        select(User).options(selectinload(User.role_info)).where(User.id == current_user.id)
    )
    user = result.scalar_one()
    return _user_to_out(user)
