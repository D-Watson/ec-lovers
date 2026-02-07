from fastapi import APIRouter

import consts
import models
import services

photo = APIRouter(
    prefix="/images",  # 所有路由自动加前缀 /lovers
    tags=["images"]  # 在 Swagger 文档中分组显示
)


@photo.post("/upload")
def profile_generator(lover_image: models.LoverAvatarRequest):
    try:
        res = services.generate_profile(lover_id=lover_image.lover_id,
                                        user_id=lover_image.user_id,
                                        prompt=lover_image.prompt)
        if res is not None:
            return models.SuccessResponse.build(data=res)
    except consts.ServiceError as e:
        error = models.BaseResponse(code=e.err_code, msg=e.err_msg)
        return error
