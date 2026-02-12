# crud.py
import logging
import uuid

from sqlalchemy.orm import Session

import consts
from models.schemas import UserAuth
from models.entities import UserCreate, UserUpdate
from datetime import datetime, timedelta, timezone
from typing import Optional
import util
import db

db = next(db.get_main_db())


# ===== 创建用户 =====
def create_user(user: UserAuth) -> UserAuth:
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        logging.error(f'[db] create user err,{e}')
        raise consts.ServiceError(consts.ErrorCode.DB_ERR)
    return user


# ===== 查询用户 =====

def get_user_by_email(email: str) -> Optional[UserAuth]:
    return db.query(UserAuth).filter(UserAuth.email == email).first()


def get_user_by_id(user_id: str) -> Optional[UserAuth]:
    return db.query(UserAuth).filter(UserAuth.user_id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[UserAuth]:
    return db.query(UserAuth).filter(UserAuth.username == username).first()


def get_user_by_email(email: str) -> Optional[UserAuth]:
    return db.query(UserAuth).filter(UserAuth.email == email).first()


# ===== 更新用户 =====
def update_user(user_id: int, user_update: UserUpdate) -> Optional[UserAuth]:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        db_user.password_hash = util.get_password_hash(update_data["password"])
        db_user.password_changed_at = datetime.now(timezone.utc)
        # 重置失败尝试
        db_user.failed_attempts = 0
        db_user.lock_until = None

    for key, value in update_data.items():
        if key != "password":  # 已处理
            setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


# ===== 登录验证 & 失败尝试处理 =====
def authenticate_user(username: str, password: str) -> Optional[UserAuth]:
    user = get_user_by_username(db, username)
    if not user:
        return None

    # 检查是否被锁定
    if user.is_locked and user.lock_until and user.lock_until > datetime.now(timezone.utc):
        raise Exception("账户已被锁定，请稍后再试")

    if not util.verify_password(password, user.password_hash):
        # 增加失败次数
        user.failed_attempts += 1
        if user.failed_attempts >= 5:  # 超过5次锁定30分钟
            user.is_locked = True
            user.lock_until = datetime.now(timezone.utc) + timedelta(minutes=30)
        db.commit()
        return None

    # 登录成功：重置失败计数
    if user.failed_attempts > 0 or user.is_locked:
        user.failed_attempts = 0
        user.is_locked = False
        user.lock_until = None
        db.commit()
        db.refresh(user)

    return user


# ===== 注销 MFA / 其他操作 =====
def disable_mfa(user_id: int):
    user = get_user_by_id(db, user_id)
    if user:
        user.mfa_secret = None
        db.commit()
        return True
    return False


# ===== （可选）软删除：通过 is_locked 标记 =====
def soft_delete_user(user_id: int):
    user = get_user_by_id(db, user_id)
    if user:
        user.is_locked = True  # 视为“删除”
        db.commit()
        return True
    return False
