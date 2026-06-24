# SECURITY-REVIEWED: 2026-06-24 | RULES: v2.6.0-draft
import redis
from datetime import timedelta
import consts
from settings import cfg

pool = redis.ConnectionPool(
    host=cfg.REDIS_HOST,
    port=cfg.REDIS_PORT,
    db=cfg.REDIS_DB,
    decode_responses=True,
    max_connections=cfg.REDIS_MAX_CONNECTIONS
)
r = redis.Redis(connection_pool=pool)


async def aset(key: str, value: str, expire: int):
    await r.set(key, value, expire=expire)


async def aget(key: str):
    return await r.get(key)


def set(key: str, value: str, ex_days: int = 0, ex_minutes: int = 0, ex_seconds: int = 0):
    ex = ex_days * 24 * 3600 + ex_minutes * 60 + ex_seconds
    print(key)
    print(ex)
    res = r.set(key, value, ex=timedelta(seconds=ex))
    print(res)


def get(key: str) -> str:
    if not r.exists(key):
        raise consts.ServiceError(consts.ErrorCode.REDIS_KEY_NOT_EXISTS)
    return r.get(key)


def delete(key: str):
    r.delete(key)
