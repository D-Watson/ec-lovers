import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
import services
from db import get_db

router = APIRouter(
    prefix="/lovers",  # 所有路由自动加前缀 /lovers
    tags=["lovers"]  # 在 Swagger 文档中分组显示
)


@router.post("/create", response_model=models.BaseResponse[models.UserLover])
def create_lover(lover: models.UserLoverCreate, db: Session = Depends(get_db)):
    logging.info(f"request={lover}")
    entity = services.lover_add(db, lover)
    if entity is None or entity.id < 0:
        return models.BaseResponse(
            code=500,
            msg='db error'
        )
    return models.BaseResponse(code=200, msg='success', data=entity)
