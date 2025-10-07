"""Anthropic integration for automatic tracking"""
import time
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..tracker import LLMScope

# Store original methods for unpatching
_original_create = None
_original_acreate = None
_tracker_instance: Optional['LLMScope'] = None


def patch_anthropic(tracker: 'LLMScope'):
    """
    Monkey-patch Anthropic client to automatically track all API calls

    Example:
        ```python
        from llmscope import LLMScope
        from llmscope.integrations import patch_anthropic
        import anthropic

        tracker = LLMScope(api_key="your-api-key")
        patch_anthropic(tracker)

        # Now all Anthropic calls are automatically tracked
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-opus-20240229",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        ```

    Args:
        tracker: LLMScope tracker instance
    """
    global _original_create, _original_acreate, _tracker_instance

    try:
        import anthropic
        from anthropic.resources import messages
    except ImportError:
        raise ImportError(
            "Anthropic package not found. Install with: pip install anthropic"
        )

    _tracker_instance = tracker

    # Store original methods
    if _original_create is None:
        _original_create = messages.Messages.create
    if _original_acreate is None:
        _original_acreate = messages.AsyncMessages.create

    # Patch sync create
    def tracked_create(self, *args, **kwargs):
        start_time = time.time()
        try:
            response = _original_create(self, *args, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)

            # Extract and track metrics
            from ..extractors import extract_anthropic_metrics
            event = extract_anthropic_metrics(response, duration_ms)

            if event and _tracker_instance:
                if _tracker_instance.project:
                    event['project_id'] = _tracker_instance.project
                if 'metadata' not in event:
                    event['metadata'] = {}
                event['metadata']['auto_tracked'] = True

                try:
                    _tracker_instance.client.events.ingest(event)
                except Exception as e:
                    if _tracker_instance.debug:
                        print(f"LLMScope tracking error: {e}")

            return response
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            if _tracker_instance:
                _tracker_instance._track_error(e, duration_ms, "anthropic.messages.create")
            raise

    # Patch async create
    async def tracked_acreate(self, *args, **kwargs):
        start_time = time.time()
        try:
            response = await _original_acreate(self, *args, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)

            # Extract and track metrics
            from ..extractors import extract_anthropic_metrics
            event = extract_anthropic_metrics(response, duration_ms)

            if event and _tracker_instance:
                if _tracker_instance.project:
                    event['project_id'] = _tracker_instance.project
                if 'metadata' not in event:
                    event['metadata'] = {}
                event['metadata']['auto_tracked'] = True

                try:
                    _tracker_instance.client.events.ingest(event)
                except Exception as e:
                    if _tracker_instance.debug:
                        print(f"LLMScope tracking error: {e}")

            return response
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            if _tracker_instance:
                _tracker_instance._track_error(e, duration_ms, "anthropic.messages.create")
            raise

    # Apply patches
    messages.Messages.create = tracked_create
    messages.AsyncMessages.create = tracked_acreate


def unpatch_anthropic():
    """
    Remove Anthropic monkey patches and restore original methods

    Example:
        ```python
        from llmscope.integrations import unpatch_anthropic

        # Restore original Anthropic behavior
        unpatch_anthropic()
        ```
    """
    global _original_create, _original_acreate, _tracker_instance

    if _original_create is None:
        return  # Not patched

    try:
        import anthropic
        from anthropic.resources import messages

        # Restore original methods
        if _original_create:
            messages.Messages.create = _original_create
        if _original_acreate:
            messages.AsyncMessages.create = _original_acreate

        # Reset globals
        _original_create = None
        _original_acreate = None
        _tracker_instance = None

    except ImportError:
        pass
