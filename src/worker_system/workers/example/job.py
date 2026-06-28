import os
import tempfile
from datetime import datetime

from sqlalchemy import update

from worker_system.core.logger import get_logger
from worker_system.core import database
from worker_system.workers.example.model import WorkerJob

logger = get_logger()


async def run_example_job(payload: dict, storage):
    logger.info("👋 Hello from example worker!")
    logger.info(f"📦 Payload recibido: {payload}")

    job_id = None

    # =========================================================
    # 🧠 CREATE JOB
    # =========================================================
    try:
        async with database.SessionLocal() as session:
            job = WorkerJob(
                job_type="process_images",
                folder_id=payload.get("folder_id"),
                status="processing",
                payload=payload,
            )

            session.add(job)
            await session.commit()
            await session.refresh(job)

            job_id = job.id

        logger.info(f"🧠 Job creado: {job_id}")

    except Exception as e:
        logger.error(f"❌ Error creando job: {e}")
        raise

    # =========================================================
    # 📂 PROCESS FILES
    # =========================================================
    results = []
    all_ok = True

    try:
        files = payload.get("files", [])

        for file_path in files:
            try:
                tmp_file = tempfile.NamedTemporaryFile(delete=False)
                tmp_path = tmp_file.name
                tmp_file.close()

                await storage.download_file(file_path, tmp_path)

                exists = os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0

                logger.info(f"📄 {file_path} → {'✅ existe' if exists else '❌ vacío'}")

                if not exists:
                    all_ok = False

                results.append(
                    {
                        "file": file_path,
                        "exists": exists,
                    }
                )

                os.remove(tmp_path)

            except Exception as e:
                logger.error(f"❌ Error con {file_path}: {e}")

                all_ok = False

                results.append(
                    {
                        "file": file_path,
                        "exists": False,
                        "error": str(e),
                    }
                )

        # =========================================================
        # ✅ UPDATE JOB
        # =========================================================
        async with database.SessionLocal() as session:
            await session.execute(
                update(WorkerJob)
                .where(WorkerJob.id == job_id)
                .values(
                    status="done" if all_ok else "failed",
                    result=results,
                    processed_at=datetime.utcnow(),
                )
            )
            await session.commit()

        logger.info("💾 Job actualizado en DB")

    except Exception as e:
        logger.error(f"💥 Job failed: {e}")

        if job_id:
            async with database.SessionLocal() as session:
                await session.execute(
                    update(WorkerJob)
                    .where(WorkerJob.id == job_id)
                    .values(
                        status="failed",
                        error=str(e),
                        processed_at=datetime.utcnow(),
                    )
                )
                await session.commit()
