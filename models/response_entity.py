from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from typing import TypeVar, Generic

T = TypeVar('T')


class BaseResponse(BaseModel,Generic[T]):
    code: int
    msg: str
    data: Optional[T] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# 分页响应格式
class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int
