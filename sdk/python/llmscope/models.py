"""Data models for LLMScope SDK"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EventRequest(BaseModel):
    """LLM event request model"""
    tenant_id: Optional[str] = None
    project_id: Optional[str] = None
    time: Optional[datetime] = None
    model: str
    provider: str
    endpoint: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tokens_prompt: int
    tokens_completion: int
    tokens_total: Optional[int] = None
    latency_ms: int
    time_to_first_token_ms: Optional[int] = None
    cost_usd: Optional[float] = None
    messages: Optional[List[Dict[str, Any]]] = None
    response: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    status: str = "success"
    error_message: Optional[str] = None
    has_error: bool = False
    pii_detected: bool = False
    metadata: Optional[Dict[str, Any]] = None


class EventResponse(BaseModel):
    """Event ingestion response"""
    status: str
    event_id: str


class BatchIngestRequest(BaseModel):
    """Batch event ingestion request"""
    events: List[EventRequest] = Field(..., min_length=1, max_length=100)


class BatchIngestResponse(BaseModel):
    """Batch ingestion response"""
    status: str
    count: int
    event_ids: List[str]


class AlertRule(BaseModel):
    """Alert rule configuration"""
    name: str
    condition: str
    threshold: float
    enabled: bool = True


class APIKeyCreate(BaseModel):
    """API key creation request"""
    name: str
    description: str = ""