"""Anthropic integration with automatic tracking"""
import time
from typing import Optional
from .tracker import LLMTracker


class AnthropicTracker:
    """Automatic tracking for Anthropic API calls"""

    def __init__(self, tracker: LLMTracker):
        """
        Initialize Anthropic tracker

        Args:
            tracker: LLMScope tracker instance
        """
        self.tracker = tracker

    def patch_anthropic(self):
        """Patch Anthropic client to automatically track calls"""
        try:
            import anthropic
            original_create = anthropic.Anthropic.messages.create

            def tracked_create(self, *args, **kwargs):
                start_time = time.time()
                response = original_create(self, *args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000

                # Extract metrics
                model = kwargs.get("model", "unknown")
                usage = response.usage

                self.tracker.track_event(
                    model=model,
                    provider="anthropic",
                    prompt_tokens=usage.input_tokens,
                    completion_tokens=usage.output_tokens,
                    latency_ms=latency_ms,
                    metadata={"request_id": response.id}
                )

                return response

            anthropic.Anthropic.messages.create = tracked_create
        except ImportError:
            print("Anthropic not installed, skipping patch")


def patch_anthropic(api_key: str, base_url: str = "http://localhost:8000"):
    """
    Convenience function to patch Anthropic with tracking

    Args:
        api_key: LLMScope API key
        base_url: LLMScope API base URL
    """
    tracker = LLMTracker(api_key, base_url)
    anthropic_tracker = AnthropicTracker(tracker)
    anthropic_tracker.patch_anthropic()
