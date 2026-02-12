# schemas.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class EmailTokenSendRequest(BaseModel):
    email: EmailStr


class UserCreate(BaseModel):
    username: str = Field(
        default='', min_length=1, max_length=20
    )
    email: EmailStr
    email_token: str = Field(
        max_length=6, min_length=6
    )
    password: str = Field(
        min_length=6, max_length=15
    )


class UserLogin(BaseModel):
    user_id: Optional[str] = Field(
        default='', min_length=1, max_length=100
    ) | None
    email: EmailStr
    username: Optional[str] = None
    password: str = Field(
        min_length=6, max_length=15
    )


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_locked: Optional[bool] = None
    mfa_secret: Optional[str] = None


class RegisterRes(BaseModel):
    user_id: int
    username: str


class LoginRes(BaseModel):
    user_id: int
    username: str
    token: str


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
