import logging

from passlib.context import CryptContext
from snowflake import SnowflakeGenerator
from db import set, get
from jose import jwt
from datetime import datetime, timedelta
from consts import ServiceError, ErrorCode

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-super-secret-key-32+chars"  # 至少 32 位
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


# ===== 密码工具 =====
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_uuid() -> int | None:
    generator = SnowflakeGenerator(42)
    unique_id = next(generator)
    return unique_id


def get_user_token_key(user_id: str):
    return f'auth:{user_id}'


def validate_token(user_id: str, token: str) -> bool:
    try:
        key = get_user_token_key(user_id)
        rtoken = get(key)
        if rtoken != token:
            return False
    except Exception as e:
        logging.error(f'validate token error, err={e}')
        return False
    return True


def create_access_token(user_id: str, username: str):
    data: dict = {"user_id": user_id, "username": username}
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})  # 设置过期时间
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def save_token(user_id: str, token: str):
    key = get_user_token_key(user_id)
    try:
        set(key, token, ex_days=30)
    except Exception as e:
        logging.error(f'[redis] save token err={e}')
        raise ServiceError(ErrorCode.REDIS_ERR)


def delete_token(user_id: str):
    key = get_user_token_key(user_id)
    try:
        set(key, '', 0)
    except Exception as e:
        logging.error(f'[redis] delete token err={e}')
        raise ServiceError(ErrorCode.REDIS_ERR)


def save_email_token(email: str, token: str):
    key = f'email_token:{email}'
    try:
        set(key, token, ex_minutes=5)  # 5分钟过期
    except Exception as e:
        logging.error(f'[redis] save email token err={e}')
        raise ServiceError(ErrorCode.REDIS_ERR)


def verify_email_token(email: str, token: str) -> bool:
    key = f'email_token:{email}'
    try:
        rtoken = get(key)
        if rtoken != token:
            return False
    except Exception as e:
        logging.error(f'[redis] verify email token err={e}')
        return False
    return True
