# settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    # 主业务库
    biz_db_host: str
    biz_db_port: int = 5432
    biz_db_user: str
    biz_db_password: str
    biz_db_name: str
    pool_size: int = 20
    max_overflow: int = 50

    @property
    def biz_database_url(self) -> str:
        return f"postgresql://{self.biz_db_user}:{self.biz_db_password}@{self.biz_db_host}:{self.biz_db_port}/{self.biz_db_name}"

    # Bot 数据库
    bot_db_host: str
    bot_db_port: int = 5432
    bot_db_user: str
    bot_db_password: str
    bot_db_name: str

    @property
    def bot_database_url(self) -> str:
        return f"postgresql://{self.bot_db_user}:{self.bot_db_password}@{self.bot_db_host}:{self.bot_db_port}/{self.bot_db_name}"

    # Message 数据库
    msg_db_host: str
    msg_db_port: int = 5432
    msg_db_user: str
    msg_db_password: str
    msg_db_name: str

    @property
    def msg_database_url(self) -> str:
        return f"postgresql://{self.msg_db_user}:{self.msg_db_password}@{self.msg_db_host}:{self.msg_db_port}/{self.msg_db_name}"


# 创建单例实例
settings = Settings()
