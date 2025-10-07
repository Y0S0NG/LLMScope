"""Unit tests for Events API"""
import pytest
from unittest.mock import Mock, patch
from llmscope.events import EventsClient
from llmscope.models import EventRequest, EventResponse, BatchIngestResponse


class TestEventsClient:
    """Test suite for EventsClient"""

    @pytest.fixture
    def client(self):
        """Create EventsClient instance"""
        return EventsClient(api_key="test-key", base_url="http://localhost:8000")

    def test_ingest_with_dict(self, client):
        """Test ingesting event with dict"""
        with patch.object(client, '_post') as mock_post:
            mock_post.return_value = {"status": "queued", "event_id": "evt_123"}

            event_data = {
                "model": "gpt-4",
                "provider": "openai",
                "tokens_prompt": 100,
                "tokens_completion": 50,
                "latency_ms": 1200
            }

            response = client.ingest(event_data)

            assert isinstance(response, EventResponse)
            assert response.event_id == "evt_123"
            assert response.status == "queued"
            mock_post.assert_called_once()

    def test_ingest_with_model(self, client):
        """Test ingesting event with EventRequest model"""
        with patch.object(client, '_post') as mock_post:
            mock_post.return_value = {"status": "queued", "event_id": "evt_456"}

            event = EventRequest(
                model="gpt-4",
                provider="openai",
                tokens_prompt=100,
                tokens_completion=50,
                latency_ms=1200
            )

            response = client.ingest(event)

            assert isinstance(response, EventResponse)
            assert response.event_id == "evt_456"
            mock_post.assert_called_once()

    def test_ingest_batch(self, client):
        """Test batch ingestion"""
        with patch.object(client, '_post') as mock_post:
            mock_post.return_value = {
                "status": "queued",
                "count": 2,
                "event_ids": ["evt_1", "evt_2"]
            }

            events = [
                {"model": "gpt-4", "provider": "openai", "tokens_prompt": 100,
                 "tokens_completion": 50, "latency_ms": 1200},
                {"model": "claude-3", "provider": "anthropic", "tokens_prompt": 150,
                 "tokens_completion": 75, "latency_ms": 1500}
            ]

            response = client.ingest_batch(events)

            assert isinstance(response, BatchIngestResponse)
            assert response.count == 2
            assert len(response.event_ids) == 2
            mock_post.assert_called_once()

    def test_get_recent(self, client):
        """Test getting recent events"""
        with patch.object(client, '_get') as mock_get:
            mock_get.return_value = [
                {"event_id": "evt_1", "model": "gpt-4"},
                {"event_id": "evt_2", "model": "claude-3"}
            ]

            events = client.get_recent(limit=50)

            assert len(events) == 2
            mock_get.assert_called_once_with("/api/v1/events/recent", params={"limit": 50})

    def test_get_stats(self, client):
        """Test getting processing stats"""
        with patch.object(client, '_get') as mock_get:
            mock_get.return_value = {
                "total_events": 1000,
                "queue_length": 5,
                "dlq_length": 0
            }

            stats = client.get_stats()

            assert stats["total_events"] == 1000
            assert stats["queue_length"] == 5
            mock_get.assert_called_once()

    def test_get_queue_stats(self, client):
        """Test getting queue stats"""
        with patch.object(client, '_get') as mock_get:
            mock_get.return_value = {"pending": 5, "processing": 2}

            queue_stats = client.get_queue_stats()

            assert queue_stats["pending"] == 5
            mock_get.assert_called_once()