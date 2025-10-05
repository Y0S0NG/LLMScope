"""Background worker for processing events from Redis queue"""
import asyncio
import json
import logging
from typing import Optional
from redis.asyncio import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from ..config import settings
from ..services.event_service import EventService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection for worker (separate from API)
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class EventProcessor:
    """Background processor for queued events"""

    def __init__(self):
        self.redis_client: Optional[Redis] = None
        self.running = False

    async def connect_redis(self):
        """Connect to Redis"""
        self.redis_client = Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info(f"Connected to Redis: {settings.redis_url}")

    async def send_to_dlq(self, event_json: str, error: str, event_id: str = "unknown"):
        """
        Send failed event to dead letter queue

        Args:
            event_json: Original event JSON
            error: Error message
            event_id: Event ID for logging
        """
        from datetime import datetime, timezone

        try:
            dlq_entry = {
                "event": event_json,
                "error": str(error),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_id": event_id
            }

            await self.redis_client.lpush(
                settings.redis_dlq_name,
                json.dumps(dlq_entry)
            )
            logger.warning(f"📮 Sent event {event_id} to DLQ: {error}")

        except Exception as dlq_error:
            logger.error(f"❌ Failed to send to DLQ: {dlq_error}")

    async def process_single_event(
        self,
        event_json: str,
        db: Session,
        retry_count: int = 0
    ) -> bool:
        """
        Process a single event from the queue with retry logic

        Args:
            event_json: JSON string of event data
            db: Database session
            retry_count: Current retry attempt (0-indexed)

        Returns:
            True if processed successfully, False otherwise
        """
        event_id = "unknown"

        try:
            event_data = json.loads(event_json)
            event_id = event_data.get("id", "unknown")

            # Store to database
            EventService.store_event(db, event_data)

            if retry_count > 0:
                logger.info(f"✅ Processed event {event_id} (after {retry_count} retries)")
            else:
                logger.info(f"✅ Processed event {event_id}")

            return True

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in queue: {e}"
            logger.error(f"❌ {error_msg}")
            # Invalid JSON cannot be retried, send directly to DLQ
            await self.send_to_dlq(event_json, error_msg, event_id)
            return False

        except Exception as e:
            error_msg = f"Failed to process event: {e}"

            # Retry logic with exponential backoff
            if retry_count < settings.worker_max_retries:
                backoff_time = settings.worker_retry_backoff_base ** retry_count
                logger.warning(
                    f"⚠️  Event {event_id} failed (attempt {retry_count + 1}/{settings.worker_max_retries + 1}). "
                    f"Retrying in {backoff_time}s..."
                )
                await asyncio.sleep(backoff_time)
                return await self.process_single_event(event_json, db, retry_count + 1)
            else:
                # Max retries exceeded, send to DLQ
                logger.error(f"❌ Event {event_id} failed after {settings.worker_max_retries + 1} attempts")
                await self.send_to_dlq(event_json, error_msg, event_id)
                return False

    async def process_batch(self, batch_size: int = 100):
        """
        Process a batch of events from the queue

        Args:
            batch_size: Number of events to process in one batch
        """
        if not self.redis_client:
            logger.error("Redis client not connected!")
            return

        # Pop multiple events at once for better performance
        events_to_process = []

        for _ in range(batch_size):
            result = await self.redis_client.rpop(settings.redis_queue_name)
            if result is None:
                break
            events_to_process.append(result)

        if not events_to_process:
            return  # Nothing to process

        # Process all events in a single database session
        db = SessionLocal()
        try:
            success_count = 0
            for event_json in events_to_process:
                if await self.process_single_event(event_json, db):
                    success_count += 1

            logger.info(f"📊 Processed {success_count}/{len(events_to_process)} events")

        finally:
            db.close()

    async def run(self):
        """
        Main worker loop

        Continuously processes events from the Redis queue
        """
        logger.info("🚀 Starting LLMScope event processor...")
        logger.info(f"   Queue: {settings.redis_queue_name}")
        logger.info(f"   Batch size: {settings.redis_queue_batch_size}")

        await self.connect_redis()
        self.running = True

        while self.running:
            try:
                # Check queue length
                queue_length = await self.redis_client.llen(settings.redis_queue_name)

                if queue_length > 0:
                    logger.debug(f"Queue length: {queue_length}")
                    await self.process_batch(settings.redis_queue_batch_size)
                else:
                    # No events, wait before polling again
                    await asyncio.sleep(settings.worker_poll_interval)

            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.running = False
                break

            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                await asyncio.sleep(1)  # Backoff on error

        # Cleanup
        if self.redis_client:
            await self.redis_client.close()

        logger.info("👋 Event processor stopped")

    async def stop(self):
        """Stop the worker gracefully"""
        self.running = False


async def main():
    """Entry point for the worker"""
    processor = EventProcessor()

    try:
        await processor.run()
    except KeyboardInterrupt:
        await processor.stop()


if __name__ == "__main__":
    asyncio.run(main())
