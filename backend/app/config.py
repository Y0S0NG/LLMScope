"""Configuration management"""
from pydantic_settings import BaseSettings
from typing import Optional
import uuid


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    api_title: str = "LLMScope API"
    api_version: str = "1.0.0"

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5433/llmscope"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_queue_name: str = "llmscope:events"
    redis_queue_batch_size: int = 100  # Process N events at once from queue
    redis_dlq_name: str = "llmscope:events:dlq"  # Dead letter queue

    # Worker Settings
    worker_poll_interval: float = 0.1  # Seconds to wait when queue is empty
    worker_max_retries: int = 3  # Max retry attempts for failed events
    worker_retry_backoff_base: float = 2.0  # Exponential backoff base (seconds)

    # Security
    secret_key: str = "change-me-in-production"
    api_key_header: str = "X-API-Key"

    # Single-Tenant Mode (MVP)
    single_tenant_mode: bool = True
    require_auth: bool = True
    api_key: str = "llmscope-local-key"  # Static API key for single-tenant mode
    default_tenant_id: str = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'llmscope.default.tenant'))
    default_project_id: str = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'llmscope.default.project'))

    # Rate Limiting
    rate_limit_requests: int = 1000
    rate_limit_period: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
