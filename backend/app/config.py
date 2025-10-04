"""Configuration management"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    api_title: str = "LLMScope API"
    api_version: str = "1.0.0"

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5433/llmscope"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Security
    secret_key: str = "change-me-in-production"
    api_key_header: str = "X-API-Key"

    # Rate Limiting
    rate_limit_requests: int = 1000
    rate_limit_period: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
