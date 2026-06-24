# SECURITY-REVIEWED: 2026-06-24 | RULES: v2.6.0-draft
import logging

from typing import Optional
from datetime import datetime, timedelta, timezone

import consts
import util
from models.schemas import UserAuth
from models.entities import UserUpdate
from db.postgre_engine import BizSessionLocal


# ===== 创建用户 =====
def create_user(user: UserAuth) -> UserAuth:
    with BizSessionLocal() as session:
        try:
            session.add(user)
            session.commit()
            session.refresh(user)
        except Exception as e:
            logging.error(f'[db] create user err,{e}')
            raise consts.ServiceError(consts.ErrorCode.DB_ERR)
        return user


# ===== 查询用户 =====
def get_user_by_email(email: str) -> Optional[UserAuth]:
    with BizSessionLocal() as session:
        return session.query(UserAuth).filter(UserAuth.email == email).first()


def get_user_by_id(user_id: str) -> Optional[UserAuth]:
    with BizSessionLocal() as session:
        return session.query(UserAuth).filter(UserAuth.user_id == user_id).first()


def get_user_by_username(username: str) -> Optional[UserAuth]:
    with BizSessionLocal() as session:
        return session.query(UserAuth).filter(UserAuth.username == username).first()


# ===== 更新用户 =====
def update_user(user_id: int, user_update: UserUpdate) -> Optional[UserAuth]:
    with BizSessionLocal() as session:
        user = session.query(UserAuth).filter(UserAuth.user_id == user_id).first()
        if not user:
            return None

        update_data = user_update.dict(exclude_unset=True)

        if “password” in update_data and update_data[“password”]:
            user.password_hash = util.get_password_hash(update_data[“password”])
            user.password_changed_at = datetime.now(timezone.utc)
            user.failed_attempts = 0
            user.lock_until = None

        for key, value in update_data.items():
            if key != “password”:
                setattr(user, key, value)

        session.commit()
        session.refresh(user)
        return user


# ===== 登录验证 & 失败尝试处理 =====
def authenticate_user(username: str, password: str) -> Optional[UserAuth]:
    with BizSessionLocal() as session:
        user = session.query(UserAuth).filter(UserAuth.username == username).first()
        if not user:
            return None

        if user.is_locked and user.lock_until and user.lock_until > datetime.now(timezone.utc):
            raise Exception(“账户已被锁定，请稍后再试”)

        if not util.verify_password(password, user.password_hash):
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.is_locked = True
                user.lock_until = datetime.now(timezone.utc) + timedelta(minutes=30)
            session.commit()
            return None

        if user.failed_attempts > 0 or user.is_locked:
            user.failed_attempts = 0
            user.is_locked = False
            user.lock_until = None
        session.commit()
        session.refresh(user)
        return user


# ===== 注销 MFA =====
def disable_mfa(user_id: int):
    with BizSessionLocal() as session:
        user = session.query(UserAuth).filter(UserAuth.user_id == user_id).first()
        if user:
            user.mfa_secret = None
            session.commit()
            return True
        return False


# ===== 软删除 =====
def soft_delete_user(user_id: int):
    with BizSessionLocal() as session:
        user = session.query(UserAuth).filter(UserAuth.user_id == user_id).first()
        if user:
            user.is_locked = True
            session.commit()
            return True
        return False
