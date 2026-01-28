from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class UserLoverBase(BaseModel):
    user_id: str
    lover_id: str
    avatar: str
    name: str = Field(..., min_length=2, max_length=10, description="用户名")
    gender: int = Field(ge=0, le=1)
    personality: int
    talking_style: int


class UserLoverCreate(UserLoverBase):
    hobbies: List[int]


class UserLover(UserLoverBase):
    id: int
    hobbies: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
