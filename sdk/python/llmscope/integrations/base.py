"""Base integration class"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tracker import LLMScope


class BaseIntegration:
    """Base class for LLM provider integrations"""

    def __init__(self, tracker: 'LLMScope'):
        """
        Initialize integration

        Args:
            tracker: LLMScope tracker instance
        """
        self.tracker = tracker
        self._original_methods = {}

    def patch(self):
        """Apply monkey patches to enable auto-tracking"""
        raise NotImplementedError("Subclasses must implement patch()")

    def unpatch(self):
        """Remove monkey patches and restore original methods"""
        raise NotImplementedError("Subclasses must implement unpatch()")
