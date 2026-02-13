from fastapi import APIRouter, Body

import consts
import models
import services
from typing import Annotated

user_router = APIRouter(
    prefix="/user",  # 所有路由自动加前缀 /lovers
    tags=["user"]  # 在 Swagger 文档中分组显示
)


@user_router.post("/login")
def login(user: models.UserLogin):
    try:
        res = services.user_login(user)
        if res is not None:
            return models.SuccessResponse.build(data=res)
    except consts.ServiceError as e:
        error = models.BaseResponse(code=e.err_code, msg=e.err_msg)
        return error


@user_router.post("/register")
def register(user: models.UserCreate):
    try:
        res = services.user_register(user)
        if res is not None:
            return models.SuccessResponse.build(data=res)
    except consts.ServiceError as e:
        error = models.BaseResponse(code=e.err_code, msg=e.err_msg)
        return error


@user_router.post("/send_email_code")
def send_email_code(email: models.EmailTokenSendRequest):
    res = services.send_verification_email(email.email)
    if res is not None:
        return models.SuccessResponse.build(data=res)
