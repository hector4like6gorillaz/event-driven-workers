from functools import lru_cache
from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =========================================================
    # 🌐 CORE
    # =========================================================
    PROJECT_NAME: str = "event-worker-template"
    ENVIRONMENT_NAME: str = "LOCALDEV"
    LOG_LEVEL: str = "DEBUG"

    # =========================================================
    # 🐇 NATS / JETSTREAM
    # =========================================================
    NATS_URL: Optional[str] = None

    # Stream donde viven los eventos
    EVENTS_STREAM: str = "example_stream"

    # Subject que consume este worker
    EXAMPLE_SUBJECT: str = "example.created"

    # Durable Consumer
    EXAMPLE_CONSUMER: str = "example-worker"

    # =========================================================
    # 🪣 STORAGE (MINIO / GCS)
    # =========================================================
    STORAGE_PROVIDER: Optional[str] = None
    STORAGE_BUCKET: Optional[str] = None

    MINIO_ENDPOINT: Optional[str] = None
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_SECURE: bool = False

    # =========================================================
    # 🗄 DATABASE
    # =========================================================
    DATABASE_URL: Optional[str] = None
    DATABASE_SCHEMA: Optional[str] = None

    # =========================================================
    # 🔐 SECURITY
    # =========================================================
    JWT_SECRET_KEY: Optional[SecretStr] = None

    # =========================================================
    # ⚙ CONFIG
    # =========================================================
    model_config = SettingsConfigDict(
        env_file=".env.localdev",
        extra="ignore",
    )

    # =========================================================
    # 🔥 LOG SUMMARY
    # =========================================================
    def log_summary(self, logger):

        logger.info(f"🌍 ENV: {self.ENVIRONMENT_NAME}")
        logger.info(f"📡 NATS: {self.NATS_URL}")
        logger.info(f"🧱 Stream: {self.EVENTS_STREAM}")
        logger.info(f"📨 Subject: {self.EXAMPLE_SUBJECT}")
        logger.info(f"👷 Consumer: {self.EXAMPLE_CONSUMER}")
        logger.info(f"🪣 Bucket: {self.STORAGE_BUCKET}")

        if not self.NATS_URL:
            logger.warning("⚠️ Missing NATS_URL")

        if not self.STORAGE_BUCKET:
            logger.warning("⚠️ Missing STORAGE_BUCKET")

        if not self.DATABASE_URL:
            logger.warning("⚠️ Missing DATABASE_URL")


# =========================================================
# 🧠 SINGLETON
# =========================================================
@lru_cache()
def get_settings() -> Settings:
    return Settings()
