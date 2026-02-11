# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserAuth(Base):
    __tablename__ = "user_auth"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Text, unique=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_locked = Column(Boolean, default=False)
    failed_attempts = Column(Integer, default=0)
    lock_until = Column(DateTime(timezone=True))
    mfa_secret = Column(String(100))
    password_changed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
