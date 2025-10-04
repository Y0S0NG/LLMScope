"""OpenAI integration with automatic tracking"""
import time
from typing import Optional
from .tracker import LLMTracker


class OpenAITracker:
    """Automatic tracking for OpenAI API calls"""

    def __init__(self, tracker: LLMTracker):
        """
        Initialize OpenAI tracker

        Args:
            tracker: LLMScope tracker instance
        """
        self.tracker = tracker

    def patch_openai(self):
        """Patch OpenAI client to automatically track calls"""
        try:
            import openai
            original_create = openai.ChatCompletion.create

            def tracked_create(*args, **kwargs):
                start_time = time.time()
                response = original_create(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000

                # Extract metrics
                model = kwargs.get("model", "unknown")
                usage = response.get("usage", {})

                self.tracker.track_event(
                    model=model,
                    provider="openai",
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    latency_ms=latency_ms,
                    metadata={"request_id": response.get("id")}
                )

                return response

            openai.ChatCompletion.create = tracked_create
        except ImportError:
            print("OpenAI not installed, skipping patch")


def patch_openai(api_key: str, base_url: str = "http://localhost:8000"):
    """
    Convenience function to patch OpenAI with tracking

    Args:
        api_key: LLMScope API key
        base_url: LLMScope API base URL
    """
    tracker = LLMTracker(api_key, base_url)
    openai_tracker = OpenAITracker(tracker)
    openai_tracker.patch_openai()
