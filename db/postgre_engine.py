# db/core.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from settings import settings

biz_engine = create_engine(
    str(settings.biz_database_url),
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    echo=False,
)
BizSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=biz_engine)

# === Bot DB 引擎 ===
bot_engine = create_engine(
    str(settings.bot_database_url),
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    echo=False,
)

BotSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=bot_engine)

# === Message DB 引擎 ===
msg_engine = create_engine(
    str(settings.msg_database_url),
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    echo=False,
)

MsgSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=msg_engine)


def get_main_db() -> Session:
    db = BizSessionLocal()
    try:
        yield db
    finally:
        db.close()


# 依赖注入函数（FastAPI 用）
def get_bot_db() -> Session:
    db = BotSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_msg_db() -> Session:
    db = MsgSessionLocal()
    try:
        yield db
    finally:
        db.close()
