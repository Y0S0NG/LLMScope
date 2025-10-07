"""Analytics API module"""
from typing import Optional
from datetime import datetime
from .client import BaseClient


class AnalyticsClient(BaseClient):
    """Client for LLMScope Analytics API"""

    def get_metrics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Get aggregated metrics

        Args:
            start_time: Start time for metrics query
            end_time: End time for metrics query
            model: Filter by specific model

        Returns:
            Dictionary with aggregated metrics

        Example:
            ```python
            from datetime import datetime, timedelta

            # Get metrics for the last 24 hours
            end = datetime.utcnow()
            start = end - timedelta(days=1)

            metrics = client.analytics.get_metrics(
                start_time=start,
                end_time=end,
                model="gpt-4"
            )

            print(f"Total requests: {metrics['total_requests']}")
            print(f"Avg latency: {metrics['avg_latency_ms']}ms")
            ```
        """
        params = {}
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
        if model:
            params["model"] = model

        return self._get("/api/v1/analytics/metrics", params=params)

    def get_costs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """
        Get cost breakdown by model/provider

        Args:
            start_time: Start time for cost query
            end_time: End time for cost query

        Returns:
            Dictionary with cost breakdown

        Example:
            ```python
            from datetime import datetime, timedelta

            # Get costs for the last 7 days
            end = datetime.utcnow()
            start = end - timedelta(days=7)

            costs = client.analytics.get_costs(
                start_time=start,
                end_time=end
            )

            print(f"Total cost: ${costs['total_cost_usd']}")
            for item in costs['by_model']:
                print(f"{item['model']}: ${item['cost_usd']}")
            ```
        """
        params = {}
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()

        return self._get("/api/v1/analytics/costs", params=params)