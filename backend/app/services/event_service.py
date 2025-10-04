"""Event service"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from ..db.models import Event
from ..core.metrics import calculate_cost


class EventService:
    """Service for handling events"""

    @staticmethod
    async def ingest_event(db: Session, event_data: Dict[str, Any]) -> Event:
        """Ingest and store event"""
        # Calculate cost if not provided
        if "cost" not in event_data:
            event_data["cost"] = calculate_cost(
                event_data["model"],
                event_data["prompt_tokens"],
                event_data["completion_tokens"]
            )

        # Create event record
        event = Event(**event_data)
        db.add(event)
        db.commit()
        db.refresh(event)

        return event

    @staticmethod
    async def get_recent_events(
        db: Session,
        limit: int = 100
    ) -> list[Event]:
        """Get recent events"""
        return db.query(Event).order_by(Event.timestamp.desc()).limit(limit).all()
