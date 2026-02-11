from fastapi import APIRouter

import consts
import models
import services

user_router = APIRouter(
    prefix="/user",  # 所有路由自动加前缀 /lovers
    tags=["user"]  # 在 Swagger 文档中分组显示
)


@user_router.post("/login")
def login(lover_image: models.LoverAvatarRequest):
    try:
        res = services.generate_profile(lover_id=lover_image.lover_id,
                                        user_id=lover_image.user_id,
                                        prompt=lover_image.prompt)
        if res is not None:
            return models.SuccessResponse.build(data=res)
    except consts.ServiceError as e:
        error = models.BaseResponse(code=e.err_code, msg=e.err_msg)
        return error


@user_router.post("/register")
def register(lover_image: models.LoverAvatarRequest):
    try:
        res = services.generate_profile(lover_id=lover_image.lover_id,
                                        user_id=lover_image.user_id,
                                        prompt=lover_image.prompt)
        if res is not None:
            return models.SuccessResponse.build(data=res)
    except consts.ServiceError as e:
        error = models.BaseResponse(code=e.err_code, msg=e.err_msg)
        return error
