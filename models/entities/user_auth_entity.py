# schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_locked: Optional[bool] = None
    mfa_secret: Optional[str] = None


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    is_locked: bool
    failed_attempts: int
    lock_until: Optional[datetime]
    mfa_secret: Optional[str]
    password_changed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
