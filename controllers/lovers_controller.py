import logging
from typing import List

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

import models
import services
import consts

router = APIRouter(
    prefix="/lovers",
    tags=["lovers"]
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
    try:
        services.save_prompt(entity)
    except consts.ServiceError as e:
        return models.BaseResponse(
            code=e.err_code,
            msg=e.err_msg
        )
    return models.SuccessResponse.build(data=entity)


@router.get("/list", response_model=models.BaseResponse[List[models.UserLover]])
def list_lovers(
        user_id: str = Query(..., min_length=1, max_length=50)
):
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


@router.post("/chat/{user_id}/{lover_id}")
async def lover_chat(
        user_id: str,
        lover_id: str,
        body: models.ChatRequest
):
    server = services.AIServer(user_id=user_id, lover_id=lover_id)
    return StreamingResponse(
        server.sse_chat(body.content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/delete")
def lover_delete(lover: models.LoverRequestBase):
    print(lover)
    try:
        if services.delete_lover(lover_id=lover.lover_id, user_id=lover.user_id):
            return models.SuccessResponse()
    except consts.ServiceError as e:
        return models.BaseResponse(
            code=e.err_code,
            msg=e.err_msg
        )


@router.get("/history")
async def get_messages(user_id: str, lover_id: str):
    try:
        res = await services.get_messages(user_id, lover_id)
        return models.SuccessResponse.build(data=res)
    except consts.ServiceError as e:
        return models.BaseResponse(
            code=e.err_code,
            msg=e.err_msg
        )
