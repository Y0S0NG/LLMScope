"""Main LLMScope SDK client"""
from .events import EventsClient
from .analytics import AnalyticsClient
from .alerts import AlertsClient
from .auth import AuthClient


class LLMScopeClient:
    """
    Main client for LLMScope API

    Provides access to all LLMScope API endpoints organized by module:
    - events: Event ingestion and retrieval
    - analytics: Metrics and cost analytics
    - alerts: Alert rule management
    - auth: API key management

    Example:
        ```python
        from llmscope import LLMScopeClient

        # Initialize client
        client = LLMScopeClient(
            api_key="your-api-key",
            base_url="http://localhost:8000"
        )

        # Ingest an event
        response = client.events.ingest({
            "model": "gpt-4",
            "provider": "openai",
            "tokens_prompt": 100,
            "tokens_completion": 50,
            "latency_ms": 1200
        })

        # Get analytics
        metrics = client.analytics.get_metrics()

        # Create alert rule
        client.alerts.create_rule({
            "name": "High Latency",
            "condition": "avg_latency_ms",
            "threshold": 2000.0
        })

        # List API keys
        keys = client.auth.list_api_keys()
        ```
    """

    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        """
        Initialize LLMScope client

        Args:
            api_key: LLMScope API key
            base_url: LLMScope API base URL (default: http://localhost:8000)
        """
        self.api_key = api_key
        self.base_url = base_url

        # Initialize sub-clients
        self.events = EventsClient(api_key=api_key, base_url=base_url)
        self.analytics = AnalyticsClient(api_key=api_key, base_url=base_url)
        self.alerts = AlertsClient(api_key=api_key, base_url=base_url)
        self.auth = AuthClient(api_key=api_key, base_url=base_url)