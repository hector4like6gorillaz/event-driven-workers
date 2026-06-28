"""
SQLAlchemy model for worker jobs registry
"""

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from worker_system.db.base import Base
from worker_system.db.database_tables import DatabaseTables
from worker_system.config.settings import get_settings


settings = get_settings()


class WorkerJob(Base):
    __tablename__ = DatabaseTables.WORKER_JOBS
    __table_args__ = {"schema": settings.DATABASE_SCHEMA}

    # =========================================================
    # 🆔 PRIMARY KEY
    # =========================================================
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # =========================================================
    # 📦 JOB INFO
    # =========================================================
    job_type = Column(String, nullable=False)  # ej: process_images
    folder_id = Column(String, nullable=True)

    status = Column(String, nullable=False, default="pending")
    # pending | processing | done | failed

    # =========================================================
    # 📡 DATA
    # =========================================================
    payload = Column(JSONB, nullable=True)
    result = Column(JSONB, nullable=True)
    error = Column(Text, nullable=True)

    # =========================================================
    # ⏱️ TIMESTAMPS
    # =========================================================
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    processed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =========================================================
    # 🔁 SERIALIZER
    # =========================================================
    def to_dict(self):
        return {
            "id": str(self.id),
            "job_type": self.job_type,
            "folder_id": self.folder_id,
            "status": self.status,
            "payload": self.payload,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "processed_at": self.processed_at,
        }
