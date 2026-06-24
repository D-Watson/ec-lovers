# SECURITY-REVIEWED: 2026-06-24 | RULES: v2.6.0-draft
import logging
from typing import List

import consts
import models
from db.postgre_engine import BizSessionLocal


# 创建
def create_user_lover(lover: models.UserLoverCreate):
    with BizSessionLocal() as session:
        db_lover = models.UserLoverDB(**lover.model_dump())
        session.add(db_lover)
        session.commit()
        session.refresh(db_lover)
        return db_lover


# 读取（单个）
def get_user_lover(user_id: str, lover_id: str):
    with BizSessionLocal() as session:
        return session.query(models.UserLoverDB).filter(
            models.UserLoverDB.user_id == user_id,
            models.UserLoverDB.lover_id == lover_id
        ).first()


# 读取（用户所有恋人）
def get_user_lovers(user_id: str) -> List[models.UserLoverDB]:
    with BizSessionLocal() as session:
        return session.query(models.UserLoverDB).filter(
            models.UserLoverDB.user_id == user_id
        ).all()


# 更新
def update_user_lover_avatar(user_id: str, lover_id: str, avatar: str):
    with BizSessionLocal() as session:
        db_lover = session.query(models.UserLoverDB).filter(
            models.UserLoverDB.user_id == user_id,
            models.UserLoverDB.lover_id == lover_id
        ).first()
        if not db_lover:
            return None
        try:
            db_lover.avatar = avatar
            session.commit()
            session.refresh(db_lover)
        except Exception as e:
            logging.error(f'update lover={lover_id} error={e}')
            raise consts.ServiceError(consts.ErrorCode.DB_ERR)
        return db_lover


# 删除
def delete_user_lover(user_id: str, lover_id: str) -> bool:
    with BizSessionLocal() as session:
        db_lover = session.query(models.UserLoverDB).filter(
            models.UserLoverDB.user_id == user_id,
            models.UserLoverDB.lover_id == lover_id
        ).first()
        if not db_lover:
            return False
        session.delete(db_lover)
        session.commit()
        return True
