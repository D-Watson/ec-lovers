import logging

from passlib.context import CryptContext

from db import set, get
from jose import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-super-secret-key-32+chars"  # 至少 32 位
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


# ===== 密码工具 =====
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


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
        set(key, token, 30*24*3600)
    except Exception as e:
        logging.error(f'[redis] save token err={e}')


