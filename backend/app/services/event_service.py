"""Event service with async Redis queue"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from redis.asyncio import Redis
import json
import uuid
from datetime import datetime, timezone

from ..db.models import LLMEvent
from ..core.metrics import calculate_cost
from ..config import settings


class EventService:
    """Service for handling events with async queue"""

    _redis_client: Optional[Redis] = None

    @classmethod
    async def get_redis(cls) -> Redis:
        """Get or create async Redis connection (singleton)"""
        if cls._redis_client is None:
            cls._redis_client = Redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return cls._redis_client

    @classmethod
    async def queue_event(cls, event_data: Dict[str, Any]) -> str:
        """
        Queue event for async processing (non-blocking, fast!)

        Args:
            event_data: Event data dictionary

        Returns:
            Event ID (UUID string)
        """
        # Calculate cost upfront (cheap operation)
        if "cost_usd" not in event_data or event_data["cost_usd"] is None:
            event_data["cost_usd"] = calculate_cost(
                event_data.get("model", ""),
                event_data.get("tokens_prompt", 0),
                event_data.get("tokens_completion", 0)
            )

        # Ensure we have an ID
        if "id" not in event_data:
            event_data["id"] = str(uuid.uuid4())

        # Ensure time is set
        if "time" not in event_data or event_data["time"] is None:
            event_data["time"] = datetime.now(timezone.utc)

        # Convert datetime to ISO string for JSON serialization
        if isinstance(event_data.get("time"), datetime):
            event_data["time"] = event_data["time"].isoformat()

        # Queue to Redis (fast, non-blocking!)
        redis_client = await cls.get_redis()
        await redis_client.lpush(
            settings.redis_queue_name,
            json.dumps(event_data, default=str)
        )

        return event_data["id"]

    @staticmethod
    def store_event(db: Session, event_data: Dict[str, Any]) -> LLMEvent:
        """
        Store event to database (used by background worker)

        Args:
            db: Database session
            event_data: Event data dictionary

        Returns:
            Saved LLMEvent instance
        """
        # Ensure ID is UUID type
        if "id" in event_data and isinstance(event_data["id"], str):
            event_data["id"] = uuid.UUID(event_data["id"])

        # Ensure tenant_id and project_id are UUID types
        if "tenant_id" in event_data and isinstance(event_data["tenant_id"], str):
            event_data["tenant_id"] = uuid.UUID(event_data["tenant_id"])
        if "project_id" in event_data and isinstance(event_data["project_id"], str):
            event_data["project_id"] = uuid.UUID(event_data["project_id"])

        # Parse time if it's a string
        if "time" in event_data and isinstance(event_data["time"], str):
            event_data["time"] = datetime.fromisoformat(event_data["time"])

        # Create event record
        event = LLMEvent(**event_data)
        db.add(event)
        db.commit()
        db.refresh(event)

        return event

    @staticmethod
    async def get_recent_events(
        db: Session,
        tenant_id: str,
        project_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent events for a tenant/project

        Args:
            db: Database session
            tenant_id: Tenant ID to filter by
            project_id: Project ID to filter by
            limit: Maximum number of events to return

        Returns:
            List of events as dictionaries
        """
        events = (
            db.query(LLMEvent)
            .filter(
                LLMEvent.tenant_id == tenant_id,
                LLMEvent.project_id == project_id
            )
            .order_by(LLMEvent.time.desc())
            .limit(limit)
            .all()
        )

        # Convert to dictionaries
        return [
            {
                "id": str(event.id),
                "time": event.time.isoformat() if event.time else None,
                "model": event.model,
                "provider": event.provider,
                "tokens_prompt": event.tokens_prompt,
                "tokens_completion": event.tokens_completion,
                "tokens_total": event.tokens_total,
                "latency_ms": event.latency_ms,
                "cost_usd": float(event.cost_usd) if event.cost_usd else None,
                "status": event.status,
                "has_error": event.has_error,
                "user_id": event.user_id,
                "session_id": event.session_id,
            }
            for event in events
        ]

    @staticmethod
    async def get_event_by_id(
        db: Session,
        event_id: str,
        tenant_id: str
    ) -> Optional[LLMEvent]:
        """
        Get event by ID (with tenant validation)

        Args:
            db: Database session
            event_id: Event ID
            tenant_id: Tenant ID for validation

        Returns:
            LLMEvent instance or None
        """
        return (
            db.query(LLMEvent)
            .filter(
                LLMEvent.id == event_id,
                LLMEvent.tenant_id == tenant_id
            )
            .first()
        )

    @classmethod
    async def get_queue_length(cls) -> int:
        """Get current queue length (for monitoring)"""
        redis_client = await cls.get_redis()
        length = await redis_client.llen(settings.redis_queue_name)
        return int(length) if length is not None else 0

    @classmethod
    async def get_dlq_length(cls) -> int:
        """Get dead letter queue length (for monitoring)"""
        redis_client = await cls.get_redis()
        length = await redis_client.llen(settings.redis_dlq_name)
        return int(length) if length is not None else 0

    @classmethod
    async def get_queue_stats(cls) -> dict:
        """
        Get comprehensive queue statistics

        Returns:
            Dictionary with queue metrics
        """
        redis_client = await cls.get_redis()

        queue_length = await redis_client.llen(settings.redis_queue_name)
        dlq_length = await redis_client.llen(settings.redis_dlq_name)

        return {
            "queue_length": int(queue_length) if queue_length is not None else 0,
            "dlq_length": int(dlq_length) if dlq_length is not None else 0,
            "queue_name": settings.redis_queue_name,
            "dlq_name": settings.redis_dlq_name
        }
