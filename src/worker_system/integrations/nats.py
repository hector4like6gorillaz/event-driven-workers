import asyncio
import json

from nats.aio.client import Client

from worker_system.core.logger import get_logger

logger = get_logger()


class NatsConsumer:

    def __init__(self, settings):

        self.settings = settings

        self.nats_url = settings.NATS_URL

        self.stream = settings.EVENTS_STREAM

        self.subject = settings.EXAMPLE_SUBJECT

        self.consumer_name = settings.EXAMPLE_CONSUMER

        self.nc = None
        self.js = None

    # =========================================================
    # 🚀 START
    # =========================================================
    async def start(self):

        logger.info(f"📡 Connecting to NATS: {self.nats_url}")

        self.nc = Client()

        await self.nc.connect(
            servers=[self.nats_url],
        )

        self.js = self.nc.jetstream()

        logger.info("✅ NATS connected")

    # =========================================================
    # ⏳ WAIT STREAM
    # =========================================================
    async def wait_for_stream(self):

        logger.info(f"⏳ Waiting Stream: {self.stream}")

        while True:

            try:

                info = await self.js.stream_info(
                    self.stream,
                )

                logger.info(f"✅ Stream ready: {info.config.name}")

                subjects = info.config.subjects or []

                if self.subject not in subjects:

                    logger.warning(
                        f"⚠️ Subject '{self.subject}' no pertenece al stream."
                    )

                else:

                    logger.info(f"✅ Subject detected: {self.subject}")

                return

            except Exception as e:

                logger.info(f"⏳ Waiting stream '{self.stream}'... ({e})")

            await asyncio.sleep(2)

    # =========================================================
    # 👂 LISTEN
    # =========================================================
    async def listen(
        self,
        handler,
    ):

        logger.info(f"👂 Listening subject: {self.subject}")

        sub = await self.js.pull_subscribe(
            subject=self.subject,
            durable=self.consumer_name,
        )

        logger.info(f"✅ Consumer ready: {self.consumer_name}")

        while True:

            try:

                messages = await sub.fetch(
                    batch=1,
                    timeout=5,
                )

                for msg in messages:

                    try:

                        payload = json.loads(msg.data.decode("utf-8"))

                        logger.info(
                            f"📥 EVENT RECEIVED\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"Subject : {msg.subject}\n"
                            f"Payload : {payload}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
                        )

                        await handler(payload)

                        await msg.ack()

                        logger.info("✅ ACK")

                    except Exception as e:

                        logger.exception(f"❌ Processing error: {e}")

                        # NO ACK
                        # JetStream hará redelivery

            except TimeoutError:

                await asyncio.sleep(1)

            except Exception as e:

                logger.exception(f"💥 Worker crash: {e}")

                await asyncio.sleep(5)

    # =========================================================
    # 🛑 STOP
    # =========================================================
    async def stop(self):

        try:

            if self.nc:

                await self.nc.close()

            logger.info("🛑 NATS disconnected")

        except Exception as e:

            logger.error(f"❌ Error closing NATS: {e}")
