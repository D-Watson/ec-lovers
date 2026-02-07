from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Any
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


class LoverRequestBase(BaseModel):
    user_id: str
    lover_id: str


class LoverAvatarRequest(BaseModel):
    user_id: str
    lover_id: str
    prompt: str


class LoverAvatarRes(BaseModel):
    user_id: str
    lover_id: str
    avatar: str


class MessageEntity(BaseModel):
    id: int
    sender: str
    content: str
    timestamp: datetime
    type: str
