import logging

import mapper
import models
import util
from models import UserCreate, RegisterRes, LoginRes
from consts import ServiceError, ErrorCode


def user_register(user: UserCreate) -> RegisterRes:
    uid = util.get_uuid()
    entity = models.UserAuth(
        user_id=uid,
        username=user.username,
        email=user.email,
        password_hash=util.get_password_hash(user.password)
    )
    try:
        res = mapper.create_user(entity)
        return RegisterRes(
            user_id=res.user_id,
            username=res.username
        )
    except ServiceError as e:
        raise e


def user_login(user: models.UserLogin) -> LoginRes:
    try:
        entity = mapper.get_user_by_id(user.user_id)
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


