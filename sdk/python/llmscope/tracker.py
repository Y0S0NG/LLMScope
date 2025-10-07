"""Auto-tracking wrapper for LLMScope SDK"""
import time
import functools
import inspect
from typing import Optional, Dict, Any, Callable
from contextlib import contextmanager
from .llmscope_client import LLMScopeClient
from .extractors import extract_openai_metrics, extract_anthropic_metrics


class TrackingSpan:
    """Context manager for tracking LLM calls"""

    def __init__(self, tracker: 'LLMScope', name: Optional[str] = None):
        self.tracker = tracker
        self.name = name
        self.start_time = None
        self.metadata = {}

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = int((time.time() - self.start_time) * 1000)

        if exc_type is not None:
            # Track error
            self._track_error(exc_val, duration_ms)

        return False  # Don't suppress exceptions

    def set_metadata(self, key: str, value: Any):
        """Set metadata for this span"""
        self.metadata[key] = value

    def track_response(self, response: Any):
        """Track LLM response"""
        duration_ms = int((time.time() - self.start_time) * 1000)

        # Try to extract metrics from response
        event = None

        # Try OpenAI format
        try:
            event = extract_openai_metrics(response, duration_ms)
        except:
            pass

        # Try Anthropic format
        if event is None:
            try:
                event = extract_anthropic_metrics(response, duration_ms)
            except:
                pass

        # If extraction worked, add metadata and ingest
        if event:
            if self.metadata:
                if event.get('metadata'):
                    event['metadata'].update(self.metadata)
                else:
                    event['metadata'] = self.metadata

            if self.tracker.project:
                event['project_id'] = self.tracker.project

            try:
                self.tracker.client.events.ingest(event)
            except Exception as e:
                # Don't fail user's code if tracking fails
                if self.tracker.debug:
                    print(f"LLMScope tracking error: {e}")

    def _track_error(self, error: Exception, duration_ms: int):
        """Track error event"""
        event = {
            "model": "unknown",
            "provider": "unknown",
            "tokens_prompt": 0,
            "tokens_completion": 0,
            "latency_ms": duration_ms,
            "status": "error",
            "error_message": str(error),
            "has_error": True,
            "metadata": self.metadata
        }

        if self.tracker.project:
            event['project_id'] = self.tracker.project

        try:
            self.tracker.client.events.ingest(event)
        except Exception as e:
            if self.tracker.debug:
                print(f"LLMScope error tracking failed: {e}")


class LLMScope:
    """
    Auto-tracking wrapper for LLMScope SDK

    Provides decorator and context manager for automatic LLM call tracking.

    Example:
        ```python
        from llmscope import LLMScope
        import openai

        # Initialize tracker
        tracker = LLMScope(
            api_key="your-api-key",
            project="production"
        )

        # Use decorator
        @tracker.trace()
        def get_completion(prompt):
            return openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )

        # Use context manager
        with tracker.track() as span:
            response = openai.chat.completions.create(...)
            span.track_response(response)
        ```
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        project: Optional[str] = None,
        debug: bool = False
    ):
        """
        Initialize LLMScope auto-tracking wrapper

        Args:
            api_key: LLMScope API key
            base_url: LLMScope API base URL
            project: Project ID for all tracked events
            debug: Enable debug logging
        """
        self.client = LLMScopeClient(api_key, base_url)
        self.project = project
        self.debug = debug

    def trace(self, name: Optional[str] = None):
        """
        Decorator for automatic LLM call tracking

        Automatically extracts metrics from OpenAI/Anthropic responses
        and sends them to LLMScope.

        Args:
            name: Optional name for the traced function

        Example:
            ```python
            @tracker.trace()
            def get_completion(prompt):
                return openai.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )

            result = get_completion("Hello!")  # Automatically tracked
            ```
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                span_name = name or func.__name__

                try:
                    result = func(*args, **kwargs)
                    duration_ms = int((time.time() - start_time) * 1000)

                    # Try to extract and track metrics from result
                    event = self._extract_event(result, duration_ms, span_name)
                    if event:
                        try:
                            self.client.events.ingest(event)
                        except Exception as e:
                            # Don't fail user's code if tracking fails
                            if self.debug:
                                print(f"LLMScope tracking error: {e}")

                    return result

                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)
                    self._track_error(e, duration_ms, span_name)
                    raise

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                span_name = name or func.__name__

                try:
                    result = await func(*args, **kwargs)
                    duration_ms = int((time.time() - start_time) * 1000)

                    # Try to extract and track metrics from result
                    event = self._extract_event(result, duration_ms, span_name)
                    if event:
                        try:
                            self.client.events.ingest(event)
                        except Exception as e:
                            # Don't fail user's code if tracking fails
                            if self.debug:
                                print(f"LLMScope tracking error: {e}")

                    return result

                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)
                    self._track_error(e, duration_ms, span_name)
                    raise

            # Return appropriate wrapper based on function type
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def track(self, name: Optional[str] = None) -> TrackingSpan:
        """
        Context manager for manual tracking

        Returns a span object that can track responses manually.

        Args:
            name: Optional name for the tracking span

        Example:
            ```python
            with tracker.track("openai_call") as span:
                span.set_metadata("user_id", "user123")
                response = openai.chat.completions.create(...)
                span.track_response(response)
            ```
        """
        return TrackingSpan(self, name)

    def _extract_event(
        self,
        result: Any,
        duration_ms: int,
        name: str
    ) -> Optional[Dict[str, Any]]:
        """Extract event data from LLM response"""
        event = None

        # Try OpenAI format
        try:
            event = extract_openai_metrics(result, duration_ms)
        except:
            pass

        # Try Anthropic format
        if event is None:
            try:
                event = extract_anthropic_metrics(result, duration_ms)
            except:
                pass

        # Add project if configured
        if event and self.project:
            event['project_id'] = self.project

        # Add function name to metadata
        if event:
            if 'metadata' not in event:
                event['metadata'] = {}
            event['metadata']['function'] = name

        return event

    def _track_error(self, error: Exception, duration_ms: int, name: str):
        """Track error event"""
        event = {
            "model": "unknown",
            "provider": "unknown",
            "tokens_prompt": 0,
            "tokens_completion": 0,
            "latency_ms": duration_ms,
            "status": "error",
            "error_message": str(error),
            "has_error": True,
            "metadata": {"function": name}
        }

        if self.project:
            event['project_id'] = self.project

        try:
            self.client.events.ingest(event)
        except Exception as e:
            if self.debug:
                print(f"LLMScope error tracking failed: {e}")
