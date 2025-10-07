"""Events API module"""
from typing import List, Optional, Union
from .client import BaseClient
from .models import EventRequest, EventResponse, BatchIngestRequest, BatchIngestResponse


class EventsClient(BaseClient):
    """Client for LLMScope Events API"""

    def ingest(self, event: Union[EventRequest, dict]) -> EventResponse:
        """
        Ingest single LLM event (non-blocking, queued for async processing)

        In single-tenant mode, tenant_id and project_id are auto-injected.
        Returns immediately after queuing the event to Redis.

        Args:
            event: Event data as EventRequest object or dict

        Returns:
            EventResponse with status and event_id

        Example:
            ```python
            from llmscope import LLMScopeClient
            from llmscope.models import EventRequest

            client = LLMScopeClient(api_key="your-api-key")

            event = EventRequest(
                model="gpt-4",
                provider="openai",
                tokens_prompt=100,
                tokens_completion=50,
                latency_ms=1200
            )

            response = client.events.ingest(event)
            print(response.event_id)
            ```
        """
        if isinstance(event, EventRequest):
            event_data = event.model_dump(exclude_none=True)
        else:
            event_data = event

        response = self._post("/api/v1/events/ingest", json=event_data)
        return EventResponse(**response)

    def ingest_batch(self, events: List[Union[EventRequest, dict]]) -> BatchIngestResponse:
        """
        Ingest multiple LLM events in a batch (non-blocking, queued)

        SDK can batch up to 100 events for efficient ingestion.
        All events are queued to Redis and return immediately.

        Args:
            events: List of event data (max 100 events)

        Returns:
            BatchIngestResponse with status, count, and event_ids

        Example:
            ```python
            events = [
                {"model": "gpt-4", "provider": "openai", "tokens_prompt": 100,
                 "tokens_completion": 50, "latency_ms": 1200},
                {"model": "claude-3", "provider": "anthropic", "tokens_prompt": 150,
                 "tokens_completion": 75, "latency_ms": 1500}
            ]

            response = client.events.ingest_batch(events)
            print(f"Ingested {response.count} events")
            ```
        """
        events_data = []
        for event in events:
            if isinstance(event, EventRequest):
                events_data.append(event.model_dump(exclude_none=True))
            else:
                events_data.append(event)

        batch_data = {"events": events_data}
        response = self._post("/api/v1/events/ingest/batch", json=batch_data)
        return BatchIngestResponse(**response)

    def get_recent(self, limit: int = 100) -> List[dict]:
        """
        Get recent events for the current tenant/project

        Args:
            limit: Maximum number of events to return (default: 100)

        Returns:
            List of recent events

        Example:
            ```python
            recent_events = client.events.get_recent(limit=50)
            for event in recent_events:
                print(event['model'], event['latency_ms'])
            ```
        """
        return self._get("/api/v1/events/recent", params={"limit": limit})

    def get_stats(self) -> dict:
        """
        Get comprehensive processing statistics

        Includes:
        - Total events stored in database
        - Current queue length (events waiting to be processed)
        - Dead letter queue length (failed events)
        - Processing lag estimate

        Returns:
            Dictionary with processing statistics

        Example:
            ```python
            stats = client.events.get_stats()
            print(f"Total events: {stats['total_events']}")
            print(f"Queue length: {stats['queue_length']}")
            ```
        """
        return self._get("/api/v1/events/stats")

    def get_queue_stats(self) -> dict:
        """
        Get queue statistics (for monitoring) - simplified version

        Returns:
            Dictionary with queue statistics

        Example:
            ```python
            queue_stats = client.events.get_queue_stats()
            print(f"Pending: {queue_stats['pending']}")
            ```
        """
        return self._get("/api/v1/events/queue/stats")