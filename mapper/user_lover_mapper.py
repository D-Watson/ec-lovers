import logging
from typing import List

import consts
import models
import db

db = next(db.get_main_db())


# 创建
def create_user_lover(lover: models.UserLoverCreate):
    db_lover = models.UserLoverDB(**lover.model_dump())
    db.add(db_lover)
    db.commit()
    db.refresh(db_lover)
    return db_lover


# 读取（单个）
def get_user_lover(user_id: str, lover_id: str):
    return db.query(models.UserLoverDB).filter(
        models.UserLoverDB.user_id == user_id,
        models.UserLoverDB.lover_id == lover_id
    ).first()


# 读取（用户所有恋人）
def get_user_lovers(user_id: str) -> List[models.UserLoverDB]:
    return db.query(models.UserLoverDB).filter(
        models.UserLoverDB.user_id == user_id
    ).all()


# 更新
def update_user_lover_avatar(user_id: str, lover_id: str, avatar: str):
    try:
        db_lover = get_user_lover(user_id, lover_id)
        if not db_lover:
            return None
        db_lover.avatar = avatar
        db.commit()
        db.refresh(db_lover)
    except Exception as e:
        logging.error(f'update lover={lover_id} error={e}')
        raise consts.ServiceError(consts.ErrorCode.DB_ERR)
    return db_lover


# 删除
def delete_user_lover(user_id: str, lover_id: str) -> bool:
    db_lover = get_user_lover(user_id, lover_id)
    if not db_lover:
        return False
    db.delete(db_lover)
    db.commit()
    return True
