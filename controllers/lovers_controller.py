import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
import services
from db import get_db
import consts

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
            code=consts.ErrorCode.DB_ERR[0],
            msg=consts.ErrorCode.DB_ERR[1]
        )
    return models.SuccessResponse.build(data=entity)


@router.get("/list", response_model=models.BaseResponse[List[models.UserLover]])
def list_lovers(user_id: str, db: Session = Depends(get_db)):
    logging.info(f"request userId={user_id}")
    try:
        list = services.lover_list(db, user_id)
    except consts.ServiceError as se:
        logging.error(f"service error code={se.err_code}, msg={se.err_msg}")
        return models.BaseResponse(
            code=se.err_code,
            msg=se.err_msg,
            data=[]
        )
    return models.SuccessResponse.build(
        data=list
    )
