"""Main SDK class for tracking LLM calls"""
import time
import requests
from typing import Optional, Dict, Any
from datetime import datetime


class LLMTracker:
    """Track LLM API calls and send to LLMScope"""

    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        """
        Initialize LLMScope tracker

        Args:
            api_key: LLMScope API key
            base_url: LLMScope API base URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def track_event(
        self,
        model: str,
        provider: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Track an LLM event

        Args:
            model: Model name (e.g., "gpt-4")
            provider: Provider name (e.g., "openai")
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            latency_ms: Latency in milliseconds
            metadata: Additional metadata
        """
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "model": model,
            "provider": provider,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "latency_ms": latency_ms,
            "metadata": metadata or {}
        }

        try:
            response = self.session.post(
                f"{self.base_url}/events/ingest",
                json=event_data,
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            # Don't fail the main application if tracking fails
            print(f"LLMScope tracking error: {e}")

    def __enter__(self):
        """Context manager entry"""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass
