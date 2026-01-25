from sqlalchemy import (
    Column, Integer, Text, Boolean, ARRAY, DateTime, text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class BotPrompt(Base):
    __tablename__ = 'bot_prompts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(Text, nullable=False)
    prompt_text = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, server_default=text('1'))
    is_active = Column(Boolean, nullable=False, server_default=text('false'))
    description = Column(Text, nullable=True)
    tags = Column(ARRAY(Text), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
