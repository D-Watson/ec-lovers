import logging
from typing import List

from fastapi import APIRouter, Depends,WebSocket
from sqlalchemy.orm import Session

import models
import services
from db import get_main_db
import consts

router = APIRouter(
    prefix="/lovers",  # 所有路由自动加前缀 /lovers
    tags=["lovers"]  # 在 Swagger 文档中分组显示
)


@router.post("/create", response_model=models.BaseResponse[models.UserLover])
def create_lover(lover: models.UserLoverCreate):
    logging.info(f"request={lover}")
    entity = services.lover_add(lover)
    if entity is None or entity.id < 0:
        return models.BaseResponse(
            code=consts.ErrorCode.DB_ERR[0],
            msg=consts.ErrorCode.DB_ERR[1]
        )
    return models.SuccessResponse.build(data=entity)


@router.get("/list", response_model=models.BaseResponse[List[models.UserLover]])
def list_lovers(user_id: str):
    logging.info(f"request userId={user_id}")
    try:
        list = services.lover_list(user_id)
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


@router.websocket("/chat/{user_id}/{lover_id}")
async def lover_chat(websocket: WebSocket,user_id: str, lover_id: str):
    await services.chat(websocket, user_id, lover_id)
