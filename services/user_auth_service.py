import logging

import mapper
import models
import util
from models import UserCreate, RegisterRes, LoginRes
from consts import ServiceError, ErrorCode


def user_register(user: UserCreate) -> RegisterRes:
    # 1.验证邮箱验证码
    try:
        res = util.verify_email_token(user.email, user.email_token)
        if not res:
            raise ServiceError(ErrorCode.EMAIL_TOKEN_ERR)
        # 2. 生成唯一uid并创建用户实体
        uid = util.get_uuid(user.email)
        entity = models.UserAuth(
            user_id=uid,
            username=user.username,
            email=user.email,
            password_hash=util.get_password_hash(user.password)
        )
        # 3. 存储用户实体
        res = mapper.create_user(entity)
        return RegisterRes(
            user_id=res.user_id,
            username=res.username
        )
    except ServiceError as e:
        logging.error(e)
        raise e


def user_login(user: models.UserLogin) -> LoginRes:
    try:
        entity = mapper.get_user_by_email(user.email)
        if not entity:
            raise ServiceError(ErrorCode.USER_NOT_FOUND)
        passwd_validated = util.verify_password(user.password, entity.password_hash)
        if not passwd_validated:
            raise ServiceError(ErrorCode.PASSWORD_ERR)
        token = util.create_access_token(entity.user_id, entity.username)
        util.save_token(entity.user_id, token)
        return LoginRes(
            user_id=entity.user_id,
            token=token,
            username=entity.username
        )
    except ServiceError as e:
        logging.error(e)
        raise e


