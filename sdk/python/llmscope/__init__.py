"""LLMScope Python SDK"""
from .llmscope_client import LLMScopeClient
from .tracker import LLMScope
from .models import (
    EventRequest,
    EventResponse,
    BatchIngestRequest,
    BatchIngestResponse,
    AlertRule,
    APIKeyCreate,
)

__version__ = "0.1.0"
__all__ = [
    "LLMScopeClient",
    "LLMScope",
    "EventRequest",
    "EventResponse",
    "BatchIngestRequest",
    "BatchIngestResponse",
    "AlertRule",
    "APIKeyCreate",
]
