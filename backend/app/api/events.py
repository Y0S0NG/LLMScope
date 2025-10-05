"""Event ingestion endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID

from ..dependencies import get_db, get_current_tenant, get_current_project
from ..db.models import Tenant, Project, LLMEvent
from ..services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])


class EventRequest(BaseModel):
    """LLM event request model"""
    # Optional - auto-filled if not provided in single-tenant mode
    tenant_id: Optional[str] = None
    project_id: Optional[str] = None

    # Timestamp (defaults to now if not provided)
    time: Optional[datetime] = None

    # Request metadata
    model: str
    provider: str
    endpoint: Optional[str] = None

    # User tracking
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Token usage
    tokens_prompt: int
    tokens_completion: int
    tokens_total: Optional[int] = None  # Auto-calculated if not provided

    # Performance metrics
    latency_ms: int
    time_to_first_token_ms: Optional[int] = None

    # Cost tracking
    cost_usd: Optional[float] = None

    # Content
    messages: Optional[List[Dict[str, Any]]] = None
    response: Optional[str] = None

    # Model parameters
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None

    # Status and flags
    status: Optional[str] = "success"
    error_message: Optional[str] = None
    has_error: bool = False
    pii_detected: bool = False

    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None


class EventResponse(BaseModel):
    """Event ingestion response"""
    status: str
    event_id: str


class BatchIngestRequest(BaseModel):
    """Batch event ingestion request"""
    events: List[EventRequest] = Field(..., min_length=1, max_length=100)


class BatchIngestResponse(BaseModel):
    """Batch ingestion response"""
    status: str
    count: int
    event_ids: List[str]


@router.post("/ingest", response_model=EventResponse)
async def ingest_event(
    event: EventRequest,
    tenant: Tenant = Depends(get_current_tenant),
    project: Project = Depends(get_current_project)
):
    """
    Ingest single LLM event (non-blocking, queued for async processing)

    In single-tenant mode, tenant_id and project_id are auto-injected.
    Returns immediately after queuing the event to Redis.
    """
    try:
        # Convert request to dict and auto-fill defaults
        event_data = event.model_dump(exclude_unset=True)

        # Auto-inject tenant and project IDs
        event_data["tenant_id"] = str(tenant.id)
        event_data["project_id"] = str(project.id)

        # Auto-calculate total tokens if not provided
        if "tokens_total" not in event_data or event_data["tokens_total"] is None:
            event_data["tokens_total"] = event.tokens_prompt + event.tokens_completion

        # Queue event (non-blocking, fast!)
        event_id = await EventService.queue_event(event_data)

        return EventResponse(
            status="accepted",
            event_id=event_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue event: {str(e)}"
        )


@router.post("/ingest/batch", response_model=BatchIngestResponse)
async def ingest_events_batch(
    request: BatchIngestRequest,
    tenant: Tenant = Depends(get_current_tenant),
    project: Project = Depends(get_current_project)
):
    """
    Ingest multiple LLM events in a batch (non-blocking, queued)

    SDK can batch up to 100 events for efficient ingestion.
    All events are queued to Redis and return immediately.
    """
    event_ids = []

    try:
        for event in request.events:
            # Convert to dict and auto-fill
            event_data = event.model_dump(exclude_unset=True)
            event_data["tenant_id"] = str(tenant.id)
            event_data["project_id"] = str(project.id)

            # Auto-calculate tokens_total
            if event_data.get("tokens_total") is None:
                event_data["tokens_total"] = (
                    event.tokens_prompt + event.tokens_completion
                )

            # Queue event (non-blocking!)
            event_id = await EventService.queue_event(event_data)
            event_ids.append(event_id)

        return BatchIngestResponse(
            status="accepted",
            count=len(event_ids),
            event_ids=event_ids
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue events: {str(e)}"
        )


@router.get("/recent")
async def get_recent_events(
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    project: Project = Depends(get_current_project)
):
    """Get recent events for the current tenant/project"""
    try:
        events = await EventService.get_recent_events(
            db,
            tenant_id=str(tenant.id),
            project_id=str(project.id),
            limit=limit
        )
        return {"events": events, "count": len(events)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch events: {str(e)}"
        )


@router.get("/stats")
async def get_processing_stats(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    project: Project = Depends(get_current_project)
):
    """
    Get comprehensive processing statistics

    Includes:
    - Total events stored in database
    - Current queue length (events waiting to be processed)
    - Dead letter queue length (failed events)
    - Processing lag estimate
    """
    try:
        # Get database counts
        total_events = db.query(LLMEvent).filter(
            LLMEvent.tenant_id == str(tenant.id),
            LLMEvent.project_id == str(project.id)
        ).count()

        # Get queue statistics
        queue_stats = await EventService.get_queue_stats()

        return {
            "total_events_stored": total_events,
            "queue_length": queue_stats["queue_length"],
            "dlq_length": queue_stats["dlq_length"],
            "processing_lag": queue_stats["queue_length"],  # Simplified: assumes 1:1
            "queue_name": queue_stats["queue_name"],
            "dlq_name": queue_stats["dlq_name"],
            "tenant_id": str(tenant.id),
            "project_id": str(project.id)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get processing stats: {str(e)}"
        )


@router.get("/queue/stats")
async def get_queue_stats(
    _tenant: Tenant = Depends(get_current_tenant)
):
    """Get queue statistics (for monitoring) - simplified version"""
    try:
        stats = await EventService.get_queue_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get queue stats: {str(e)}"
        )
