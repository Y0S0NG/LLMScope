"""Integration tests for LLMScope SDK

These tests require a running LLMScope API server.
Run with: pytest tests/test_integration.py -v

For single-tenant mode (default):
  Uses LLMSCOPE_API_KEY=llmscope-local-key (or set environment variable)

Set environment variables to override:
  LLMSCOPE_API_KEY=your-api-key
  LLMSCOPE_BASE_URL=http://localhost:8000 (optional)
"""
import pytest
import os
from llmscope import LLMScopeClient, EventRequest, AlertRule, APIKeyCreate
from datetime import datetime, timedelta


@pytest.fixture
def client():
    """Create LLMScope client - uses single-tenant default if not set"""
    api_key = os.getenv("LLMSCOPE_API_KEY", "llmscope-local-key")
    base_url = os.getenv("LLMSCOPE_BASE_URL", "http://localhost:8000")
    return LLMScopeClient(api_key=api_key, base_url=base_url)


class TestEventsIntegration:
    """Integration tests for Events API"""

    def test_ingest_single_event(self, client):
        """Test ingesting a single event"""
        event = EventRequest(
            model="gpt-4",
            provider="openai",
            tokens_prompt=100,
            tokens_completion=50,
            latency_ms=1200,
            user_id="test-user",
            metadata={"test": "integration"}
        )

        response = client.events.ingest(event)

        assert response.status == "queued"
        assert response.event_id is not None
        print(f"✅ Event ingested: {response.event_id}")

    def test_ingest_batch(self, client):
        """Test batch ingestion"""
        events = [
            {
                "model": "gpt-4",
                "provider": "openai",
                "tokens_prompt": 100,
                "tokens_completion": 50,
                "latency_ms": 1200
            },
            {
                "model": "claude-3-opus",
                "provider": "anthropic",
                "tokens_prompt": 150,
                "tokens_completion": 75,
                "latency_ms": 1500
            }
        ]

        response = client.events.ingest_batch(events)

        assert response.status == "queued"
        assert response.count == 2
        assert len(response.event_ids) == 2
        print(f"✅ Batch ingested: {response.count} events")

    def test_get_recent_events(self, client):
        """Test getting recent events"""
        events = client.events.get_recent(limit=10)

        assert isinstance(events, list)
        print(f"✅ Retrieved {len(events)} recent events")

    def test_get_stats(self, client):
        """Test getting processing stats"""
        stats = client.events.get_stats()

        assert "total_events" in stats or "queue_length" in stats
        print(f"✅ Stats: {stats}")


# NOTE: Analytics, Alerts, and Auth APIs are not fully implemented yet
# They return placeholder/TODO responses, so integration tests are skipped

@pytest.mark.skip(reason="Analytics API not fully implemented - returns placeholder data")
class TestAnalyticsIntegration:
    """Integration tests for Analytics API (SKIPPED - not implemented)"""

    def test_get_metrics(self, client):
        """Test getting metrics"""
        end = datetime.utcnow()
        start = end - timedelta(days=1)

        metrics = client.analytics.get_metrics(
            start_time=start,
            end_time=end
        )

        assert isinstance(metrics, dict)
        print(f"✅ Metrics: {metrics}")

    def test_get_costs(self, client):
        """Test getting cost breakdown"""
        end = datetime.utcnow()
        start = end - timedelta(days=7)

        costs = client.analytics.get_costs(
            start_time=start,
            end_time=end
        )

        assert isinstance(costs, dict)
        print(f"✅ Costs: {costs}")


@pytest.mark.skip(reason="Alerts API not fully implemented - returns placeholder data")
class TestAlertsIntegration:
    """Integration tests for Alerts API (SKIPPED - not implemented)"""

    def test_list_alert_rules(self, client):
        """Test listing alert rules"""
        rules = client.alerts.list_rules()

        assert isinstance(rules, list)
        print(f"✅ Retrieved {len(rules)} alert rules")

    def test_create_alert_rule(self, client):
        """Test creating an alert rule"""
        rule = AlertRule(
            name=f"Test Alert {datetime.utcnow().isoformat()}",
            condition="avg_latency_ms",
            threshold=2000.0,
            enabled=True
        )

        created_rule = client.alerts.create_rule(rule)

        assert isinstance(created_rule, dict)
        print(f"✅ Created alert rule: {created_rule}")


@pytest.mark.skip(reason="Auth API not fully implemented - returns placeholder data")
class TestAuthIntegration:
    """Integration tests for Auth API (SKIPPED - not implemented)"""

    def test_list_api_keys(self, client):
        """Test listing API keys"""
        keys = client.auth.list_api_keys()

        assert isinstance(keys, list)
        print(f"✅ Retrieved {len(keys)} API keys")

    def test_create_api_key(self, client):
        """Test creating an API key"""
        key = APIKeyCreate(
            name=f"Test Key {datetime.utcnow().isoformat()}",
            description="Integration test key"
        )

        created_key = client.auth.create_api_key(key)

        assert "key" in created_key
        print(f"✅ Created API key: {created_key['name']}")
        print(f"   Key: {created_key['key']}")