import logging

from sqlalchemy.orm import Session
import consts
import models
import mapper


def lover_add(db: Session, lover: models.UserLoverCreate):
    try:
        entity = mapper.create_user_lover(db, lover)
        userLover = entity.toUserLover()
        return userLover
    except Exception as e:
        logging.error(f"Database integrity error: {e}")
        return None


def lover_list(db: Session, user_id: str):
    res = []
    try:
        list = mapper.get_user_lovers(db, user_id)
        for item in list:
            res.append(item.toUserLover())
    except Exception as e:
        logging.error(f"Db query list error: {e}")
        raise consts.ServiceError(code=consts.ErrorCode.DB_ERR)
    return res
