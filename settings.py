# SECURITY-REVIEWED: 2026-06-24 | RULES: v2.6.0-draft
from functools import cached_property
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
import logging
import sys


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # === 数据库 ===
    biz_db_host: str
    biz_db_port: int = 5432
    biz_db_user: str
    biz_db_password: str
    biz_db_name: str
    pool_size: int = 20
    max_overflow: int = 50

    msg_db_host: str
    msg_db_port: int = 5432
    msg_db_user: str
    msg_db_password: str
    msg_db_name: str

    @property
    def biz_database_url(self) -> str:
        return f"postgresql://{self.biz_db_user}:{self.biz_db_password}@{self.biz_db_host}:{self.biz_db_port}/{self.biz_db_name}"

    @property
    def msg_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.msg_db_user}:{self.msg_db_password}@{self.msg_db_host}:{self.msg_db_port}/{self.msg_db_name}"

    # === Redis ===
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 20

    # === JWT ===
    JWT_SECRET_KEY: str = "your-super-secret-key-32+chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 30

    # === 腾讯云 COS ===
    COS_SK: str
    COS_ID: str
    COS_BUCKET: str = "images-1304897416"
    COS_REGION: str = "ap-guangzhou"

    @cached_property
    def cos_client(self) -> "CosS3Client":
        from qcloud_cos import CosConfig, CosS3Client

        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        config = CosConfig(
            Region=self.COS_REGION,
            SecretId=self.COS_ID,
            SecretKey=self.COS_SK,
            Token=None,
            Scheme='https'
        )
        return CosS3Client(config)

    # === 豆包 ARK ===
    ARK_API_KEY: str
    ARK_API_URL: str

    # === 图片生成 ===
    IMAGE_MODEL: str = "doubao-seedream-4-5-251128"
    IMAGE_SIZE: str = "2K"

    # === 邮件 ===
    EMAIL_SENDER: str = "3833340167@qq.com"
    EMAIL_PASSWORD: str = "fozjzfutbeddcgfc"
    EMAIL_SMTP_HOST: str = "smtp.qq.com"
    EMAIL_SMTP_PORT: int = 465

    # === Ollama ===
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_MAX_TOKENS: int = 1024

    # === 服务器 ===
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8080

    # === CORS ===
    CORS_ALLOW_ORIGINS: List[str] = ["*"]

    # === 认证白名单 ===
    PUBLIC_PATHS: List[str] = ["/metrics", "/user/login", "/user/register", "/user/send_email_code"]


cfg = Settings()