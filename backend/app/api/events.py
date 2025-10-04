"""Event ingestion endpoints"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/events", tags=["events"])


class Event(BaseModel):
    """LLM event model"""
    timestamp: datetime
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/ingest")
async def ingest_event(event: Event):
    """Ingest LLM event"""
    # TODO: Implement event ingestion
    return {"status": "accepted", "event_id": "placeholder"}
