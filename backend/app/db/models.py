"""SQLAlchemy models based on database-structure.md"""
from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base
import uuid


class Tenant(Base):
    """Tenant model (B2B multi-tenancy)"""
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False)
    plan = Column(String(50), default='free')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(JSONB, default={})
    usage_limits = Column(JSONB, default={"requests": 10000, "cost": 100})

    # Relationships
    projects = relationship("Project", back_populates="tenant", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="tenant", cascade="all, delete-orphan")


class Project(Base):
    """Project model"""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(JSONB, default={})

    # Relationships
    tenant = relationship("Tenant", back_populates="projects")


class LLMEvent(Base):
    """LLM events hypertable model"""
    __tablename__ = "llm_events"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Request metadata
    model = Column(String(50), index=True)
    provider = Column(String(50), index=True)
    endpoint = Column(String(255))

    # User tracking
    user_id = Column(String(255), index=True)
    session_id = Column(String(255), index=True)

    # Token usage
    tokens_prompt = Column(Integer)
    tokens_completion = Column(Integer)
    tokens_total = Column(Integer)

    # Performance metrics
    latency_ms = Column(Integer)
    time_to_first_token_ms = Column(Integer)

    # Cost tracking
    cost_usd = Column(DECIMAL(10, 6))

    # Content (compressed)
    messages = Column(JSONB)
    response = Column(Text)

    # Model parameters
    temperature = Column(DECIMAL(3, 2))
    max_tokens = Column(Integer)
    top_p = Column(DECIMAL(3, 2))

    # Status and flags
    status = Column(String(20))
    error_message = Column(Text)
    has_error = Column(Boolean, default=False)
    pii_detected = Column(Boolean, default=False)


class Alert(Base):
    """Alerts configuration"""
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255))
    condition = Column(JSONB, nullable=False)
    actions = Column(JSONB, nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="alerts")
    history = relationship("AlertHistory", back_populates="alert", cascade="all, delete-orphan")


class AlertHistory(Base):
    """Alert history"""
    __tablename__ = "alert_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey('alerts.id', ondelete='CASCADE'), nullable=False)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    event_data = Column(JSONB)
    status = Column(String(50))

    # Relationships
    alert = relationship("Alert", back_populates="history")
