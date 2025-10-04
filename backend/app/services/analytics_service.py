"""Analytics service"""
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..db import queries


class AnalyticsService:
    """Service for analytics queries"""

    @staticmethod
    async def get_metrics(
        db: Session,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get aggregated metrics"""
        return queries.get_metrics(db, start_time, end_time, model)

    @staticmethod
    async def get_cost_breakdown(
        db: Session,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> list[Dict[str, Any]]:
        """Get cost breakdown"""
        return queries.get_cost_breakdown(db, start_time, end_time)
