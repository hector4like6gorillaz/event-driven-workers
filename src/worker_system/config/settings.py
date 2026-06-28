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
    # 📬 PUB/SUB
    # =========================================================
    GCP_PROJECT_ID: Optional[str] = None 

    PUBSUB_EMULATOR_HOST: Optional[str] = None

    EXAMPLE_SUBSCRIPTION_ID: Optional[str] = None

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
    # 🗄️ DATABASE (opcional)
    # =========================================================
    DATABASE_URL: Optional[str] = None
    DATABASE_SCHEMA: Optional[str] = None

    # =========================================================
    # 🔐 SECURITY (opcional)
    # =========================================================
    JWT_SECRET_KEY: Optional[SecretStr] = None

    # =========================================================
    # ⚙️ CONFIG
    # =========================================================
    model_config = SettingsConfigDict(
        env_file=".env.localdev",
        extra="ignore",
    )

    # =========================================================
    # 🔥 VALIDACIONES SUAVES
    # =========================================================
    def log_summary(self, logger):
        logger.info(f"🌍 ENV: {self.ENVIRONMENT_NAME}")
        logger.info(f"📡 PUBSUB: {self.PUBSUB_EMULATOR_HOST}")
        logger.info(f"📦 BUCKET: {self.STORAGE_BUCKET}")

        if not self.GCP_PROJECT_ID:
            logger.warning("⚠️ Missing GCP_PROJECT_ID")

        if not self.EXAMPLE_SUBSCRIPTION_ID:
            logger.warning("⚠️ Missing EXAMPLE_SUBSCRIPTION_ID")


# =========================================================
# 🧠 SINGLETON
# =========================================================
@lru_cache()
def get_settings() -> Settings:
    return Settings()
