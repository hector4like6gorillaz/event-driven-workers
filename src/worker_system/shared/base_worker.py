import asyncio
from worker_system.core.logger import get_logger
from worker_system.core.database import init_db
from worker_system.integrations.storage import StorageService


class BaseWorker:
    def __init__(
        self,
        settings,
        consumer,
        job_handler,
        use_db=True,
        use_storage=False,
    ):
        self.settings = settings
        self.logger = get_logger()

        self.consumer = consumer
        self.job_handler = job_handler

        self.use_db = use_db
        self.use_storage = use_storage

        self.storage = None

        self.semaphore = asyncio.Semaphore(3)

    # =========================================================
    # ⚙️ SETUP
    # =========================================================
    async def setup(self):
        self.logger.info("⚙️ Initializing worker infrastructure...")

        # 🔥 DB
        if self.use_db:
            db_ok = await init_db()

            if not db_ok:
                self.logger.warning("⚠️ Running WITHOUT database")

        # 🔥 STORAGE
        if self.use_storage:
            self.logger.info("🪣 Initializing storage...")

            self.storage = StorageService(self.settings)
            await self.storage.start()

            self.logger.info("✅ Storage ready")

        self.logger.info("✅ Worker setup complete")

    # =========================================================
    # 🚀 START
    # =========================================================
    async def start(self):
        self.logger.info("🚀 Worker starting...")

        await self.setup()

        # 👇 si hay storage, lo inyectamos al handler
        if self.storage:
            handler = lambda payload: self.job_handler(payload, self.storage)
        else:
            handler = self.job_handler

        await self.consumer.wait_for_subscription()
        await self.consumer.listen(handler)
