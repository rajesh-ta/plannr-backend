from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserOut


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "member"


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleAuthRequest(BaseModel):
    credential: str  # Google ID token from frontend


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
