# db/core.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import cfg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

biz_engine = create_engine(
    str(cfg.biz_database_url),
    pool_size=cfg.pool_size,
    max_overflow=cfg.max_overflow,
    echo=False,
)
BizSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=biz_engine)

# === Message DB 引擎 ===
msg_engine = create_async_engine(
    str(cfg.msg_database_url),
    pool_size=cfg.pool_size,
    max_overflow=cfg.max_overflow,
    echo=False,
)


AsyncMsgSessionFactory = async_sessionmaker(
    bind=msg_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_msg_session():
    return AsyncMsgSessionFactory
