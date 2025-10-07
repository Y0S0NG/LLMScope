"""Unit tests for Analytics API"""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from llmscope.analytics import AnalyticsClient


class TestAnalyticsClient:
    """Test suite for AnalyticsClient"""

    @pytest.fixture
    def client(self):
        """Create AnalyticsClient instance"""
        return AnalyticsClient(api_key="test-key", base_url="http://localhost:8000")

    def test_get_metrics_no_filters(self, client):
        """Test getting metrics without filters"""
        with patch.object(client, '_get') as mock_get:
            mock_get.return_value = {
                "total_requests": 500,
                "avg_latency_ms": 1250.5,
                "total_tokens": 50000
            }

            metrics = client.get_metrics()

            assert metrics["total_requests"] == 500
            assert metrics["avg_latency_ms"] == 1250.5
            mock_get.assert_called_once_with("/api/v1/analytics/metrics", params={})

    def test_get_metrics_with_filters(self, client):
        """Test getting metrics with time and model filters"""
        with patch.object(client, '_get') as mock_get:
            mock_get.return_value = {"total_requests": 100}

            end = datetime.utcnow()
            start = end - timedelta(days=1)

            metrics = client.get_metrics(
                start_time=start,
                end_time=end,
                model="gpt-4"
            )

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args.kwargs['params']
            assert "start_time" in params
            assert "end_time" in params
            assert params["model"] == "gpt-4"

    def test_get_costs_no_filters(self, client):
        """Test getting costs without filters"""
        with patch.object(client, '_get') as mock_get:
            mock_get.return_value = {
                "total_cost_usd": 123.45,
                "by_model": [
                    {"model": "gpt-4", "cost_usd": 100.0},
                    {"model": "claude-3", "cost_usd": 23.45}
                ]
            }

            costs = client.get_costs()

            assert costs["total_cost_usd"] == 123.45
            assert len(costs["by_model"]) == 2
            mock_get.assert_called_once_with("/api/v1/analytics/costs", params={})

    def test_get_costs_with_time_range(self, client):
        """Test getting costs with time range"""
        with patch.object(client, '_get') as mock_get:
            mock_get.return_value = {"total_cost_usd": 50.0}

            end = datetime.utcnow()
            start = end - timedelta(days=7)

            costs = client.get_costs(start_time=start, end_time=end)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args.kwargs['params']
            assert "start_time" in params
            assert "end_time" in params