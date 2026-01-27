import asyncio
import logging

import consts
import models
import mapper


def lover_add(lover: models.UserLoverCreate):
    try:
        entity = mapper.create_user_lover(lover)
        userLover = entity.toUserLover()
        return userLover
    except Exception as e:
        logging.error(f"Database integrity error: {e}")
        return None


def lover_list(user_id: str):
    res = []
    try:
        list = mapper.get_user_lovers(user_id)
        for item in list:
            res.append(item.toUserLover())
    except Exception as e:
        logging.error(f"Db query list error: {e}")
        raise consts.ServiceError(code=consts.ErrorCode.DB_ERR)
    return res
