# db/core.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from settings import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

biz_engine = create_engine(
    str(settings.biz_database_url),
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    echo=False,
)
BizSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=biz_engine)

# === Message DB 引擎 ===
msg_engine = create_async_engine(
    str(settings.msg_database_url),
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    echo=False,
)


def get_main_db() -> Session:
    db = BizSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_msg_session():
    AsyncSessionLocal = async_sessionmaker(
        bind=msg_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    return AsyncSessionLocal
