# models.py
from sqlalchemy import (
    Column, BigInteger, String, Text, JSON, DateTime, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class MessageStore(Base):
    __tablename__ = 'message_store'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(128), nullable=False)
    type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    additional_kwargs = Column(JSON, nullable=False, server_default='{}')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # 在模型中也可以定义 CHECK 约束（可选，表已通过 SQL 定义）
    __table_args__ = (
        CheckConstraint(
            "type IN ('human', 'ai', 'system', 'tool', 'function')",
            name='valid_message_type'
        ),
    )
