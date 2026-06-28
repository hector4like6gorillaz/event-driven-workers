import asyncio

from worker_system.config.settings import get_settings
from worker_system.integrations.nats import NatsConsumer
from worker_system.shared.base_worker import BaseWorker
from worker_system.workers.example.job import run_example_job
from worker_system.core.logger import get_logger


async def main():
    logger = get_logger()
    settings = get_settings()

    logger.info("🚀 Starting Worker-example...")
    logger.info(f"Environment: {settings.ENVIRONMENT_NAME}")

    consumer = NatsConsumer(settings)

    worker = BaseWorker(
        settings=settings,
        consumer=consumer,
        job_handler=run_example_job,
        use_db=True,
        use_storage=True,
    )

    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())