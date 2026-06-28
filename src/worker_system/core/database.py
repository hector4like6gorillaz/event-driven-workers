import os
import asyncio
from typing import Optional, Any

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy import text

from google.cloud.sql.connector import Connector

from worker_system.config.settings import get_settings
from worker_system.core.logger import get_logger

logger = get_logger()
settings = get_settings()

engine = None
SessionLocal = None
connector: Optional[Connector] = None


# =========================================================
# 🔌 CLOUD SQL CONNECTION
# =========================================================
async def _get_cloud_connection() -> Any:
    global connector

    loop = asyncio.get_running_loop()

    if connector is None:
        logger.info("🔌 Initializing Cloud SQL Connector...")
        try:
            connector = Connector(loop=loop)
        except TypeError:
            connector = Connector()

    return await connector.connect_async(
        settings.CLOUDSQL_INSTANCE_CONNECTION_NAME,
        "asyncpg",
        user=settings.CLOUDSQL_DB_USER,
        password=settings.CLOUDSQL_DB_PASS.get_secret_value(),
        db=settings.CLOUDSQL_DB_NAME,
    )


# =========================================================
# 🔍 VALIDACIONES
# =========================================================
def _validate_cloud_config():
    required = {
        "CLOUDSQL_INSTANCE_CONNECTION_NAME": settings.CLOUDSQL_INSTANCE_CONNECTION_NAME,
        "CLOUDSQL_DB_USER": settings.CLOUDSQL_DB_USER,
        "CLOUDSQL_DB_PASS": settings.CLOUDSQL_DB_PASS,
        "CLOUDSQL_DB_NAME": settings.CLOUDSQL_DB_NAME,
    }

    missing = [k for k, v in required.items() if not v]

    if missing:
        logger.warning(f"⚠️ Missing CloudSQL vars: {missing}")
        return False

    return True


def _credentials_exist():
    path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not path:
        logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS not set")
        return False

    if not os.path.exists(path):
        logger.warning(f"⚠️ Credentials file not found at: {path}")
        return False

    logger.info(f"🔑 Using GCP credentials at: {path}")
    return True


# =========================================================
# 🚀 INIT DB
# =========================================================
async def init_db():
    global engine, SessionLocal

    logger.info("🧠 DB Strategy: LOCAL → CLOUD → NONE")

    # 🟢 LOCAL
    if settings.DATABASE_URL:
        logger.info("🟢 Using LOCAL PostgreSQL")

        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
        )

    # ☁️ CLOUD
    else:
        logger.info("🔎 No DATABASE_URL → trying CloudSQL...")

        if not _validate_cloud_config():
            logger.warning("❌ CloudSQL config incomplete")
            return False

        if not _credentials_exist():
            logger.warning("❌ Skipping CloudSQL (no credentials)")
            return False

        logger.info("☁️ Using CLOUD SQL (GCP)")

        engine = create_async_engine(
            "postgresql+asyncpg://",
            async_creator=_get_cloud_connection,
            echo=False,
            pool_pre_ping=True,
        )

    # 🔗 SESSION
    SessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # 🧪 TEST
    try:
        logger.info("🧪 Testing database connection...")

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        logger.info("✅ Database connection OK")
        return True

    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
