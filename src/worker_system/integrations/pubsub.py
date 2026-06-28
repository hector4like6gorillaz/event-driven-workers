import asyncio
import json
from typing import Callable, Awaitable

from google.cloud import pubsub_v1
from google.api_core import exceptions

from worker_system.core.logger import get_logger


logger = get_logger()


class PubSubConsumer:
    def __init__(self, settings):
        self.settings = settings

        self.project_id = settings.GCP_PROJECT_ID
        self.subscription_id = settings.EXAMPLE_SUBSCRIPTION_ID

        if settings.PUBSUB_EMULATOR_HOST:
            self.subscriber = pubsub_v1.SubscriberClient(
                client_options={"api_endpoint": settings.PUBSUB_EMULATOR_HOST}
            )
        else:
            self.subscriber = pubsub_v1.SubscriberClient()

        self.subscription_path = self.subscriber.subscription_path(
            self.project_id,
            self.subscription_id,
        )

    # =========================================================
    # ⏳ WAIT FOR SUBSCRIPTION
    # =========================================================
    async def wait_for_subscription(self):
        logger.info(
            f"⏳ Waiting for subscription: {self.subscription_id} "
            f"(project: {self.project_id})"
        )

        while True:
            try:
                await asyncio.to_thread(
                    self.subscriber.get_subscription,
                    request={"subscription": self.subscription_path},
                )

                logger.info("✅ Subscription ready")
                return

            except Exception:
                logger.warning("⏳ Not ready, retrying in 2s...")
                await asyncio.sleep(2)

    # =========================================================
    # 🔁 LISTEN LOOP
    # =========================================================
    async def listen(self, handler: Callable[[dict], Awaitable[None]]):
        logger.info(f"👂 Listening to {self.subscription_id}")

        while True:
            try:
                response = await asyncio.to_thread(
                    self.subscriber.pull,
                    request={
                        "subscription": self.subscription_path,
                        "max_messages": 1,
                    },
                    timeout=5.0,
                )

                if not response.received_messages:
                    await asyncio.sleep(1)
                    continue

                for msg in response.received_messages:
                    try:
                        data = json.loads(msg.message.data.decode("utf-8"))

                        await handler(data)

                        await asyncio.to_thread(
                            self.subscriber.acknowledge,
                            request={
                                "subscription": self.subscription_path,
                                "ack_ids": [msg.ack_id],
                            },
                        )

                        logger.info("✅ ACK")

                    except Exception as e:
                        logger.error(f"❌ Processing error: {e}")

            except (exceptions.DeadlineExceeded, TimeoutError):
                continue

            except Exception as e:
                logger.error(f"💥 Worker crash: {e}")
                await asyncio.sleep(5)
