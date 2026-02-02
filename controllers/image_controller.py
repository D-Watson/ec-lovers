import logging
import json
from fastapi import APIRouter, Request

from fastapi.responses import StreamingResponse

import consts
import models
import services

router = APIRouter(
    prefix="/images",  # 所有路由自动加前缀 /lovers
    tags=["images"]  # 在 Swagger 文档中分组显示
)


@router.post("/upload")
async def profile_generator(
        request: Request,
        lover_image: models.LoverAvatarRequest):
    async def event_generator():
        server = services.AIServer(user_id=lover_image.user_id,
                                   lover_id=lover_image.lover_id)
        if await request.is_disconnected():
            logging.info(f'request is closed')
            return
        try:
            res = await server.update_profile(lover_image)
            if res is not None:
                yield f"data: {json.dumps(models.SuccessResponse(data=res).model_dump())}\n\n"
        except consts.ServiceError as e:
            error = models.BaseResponse(code=e.err_code, msg=e.err_msg).model_dump()
            yield f"data: {json.dumps(error, ensure_ascii=False)}\n\n"
    # FastAPI 中实现 SSE（Server-Sent Events）的标准方式
    return StreamingResponse(event_generator(), media_type="text/event-stream")
