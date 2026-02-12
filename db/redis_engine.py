import redis
from datetime import timedelta
import consts

pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,  # 自动将 bytes 转为 str（避免 b'xxx'）
    max_connections=20  # 最大连接数
)
r = redis.Redis(connection_pool=pool)


async def aset(key: str, value: str, expire: int):
    await r.set(key, value, expire=expire)


async def aget(key: str):
    return await r.get(key)


def set(key: str, value: str, ex_days: int = 0, ex_minutes: int = 0, ex_seconds: int = 0):
    ex = ex_days * 24 * 3600 + ex_minutes * 60 + ex_seconds
    r.set(key, value, ex=timedelta(seconds=ex))


def get(key: str) -> str:
    if not r.exists(key):
        raise consts.ServiceError(consts.ErrorCode.REDIS_KEY_NOT_EXISTS)
    return r.get(key)


def delete(key: str):
    r.delete(key)
