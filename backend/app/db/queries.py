"""Complex database queries"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import Event, APIKey, AlertRule


def get_metrics(
    db: Session,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """Get aggregated metrics"""
    query = db.query(
        func.count(Event.id).label("total_requests"),
        func.sum(Event.total_tokens).label("total_tokens"),
        func.sum(Event.cost).label("total_cost"),
        func.avg(Event.latency_ms).label("avg_latency_ms")
    )

    if start_time:
        query = query.filter(Event.timestamp >= start_time)
    if end_time:
        query = query.filter(Event.timestamp <= end_time)
    if model:
        query = query.filter(Event.model == model)

    result = query.first()

    return {
        "total_requests": result.total_requests or 0,
        "total_tokens": result.total_tokens or 0,
        "total_cost": float(result.total_cost or 0),
        "avg_latency_ms": float(result.avg_latency_ms or 0)
    }


def get_cost_breakdown(
    db: Session,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """Get cost breakdown by model and provider"""
    query = db.query(
        Event.model,
        Event.provider,
        func.count(Event.id).label("requests"),
        func.sum(Event.cost).label("total_cost")
    ).group_by(Event.model, Event.provider)

    if start_time:
        query = query.filter(Event.timestamp >= start_time)
    if end_time:
        query = query.filter(Event.timestamp <= end_time)

    results = query.all()

    return [
        {
            "model": r.model,
            "provider": r.provider,
            "requests": r.requests,
            "total_cost": float(r.total_cost or 0)
        }
        for r in results
    ]
