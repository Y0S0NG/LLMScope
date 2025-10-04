"""SQLAlchemy models"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from .base import Base


class Event(Base):
    """LLM event model"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    model = Column(String(100), index=True)
    provider = Column(String(50), index=True)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    latency_ms = Column(Float)
    cost = Column(Float)
    metadata = Column(JSON)
    api_key_id = Column(Integer, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class APIKey(Base):
    """API key model"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(64), unique=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True))


class AlertRule(Base):
    """Alert rule model"""
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    condition = Column(String(200))
    threshold = Column(Float)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
