"""API key validation and security"""
import hashlib
import secrets
from typing import Optional


def generate_api_key() -> str:
    """Generate a secure API key"""
    return f"llmscope_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def validate_api_key(api_key: str, hashed_key: str) -> bool:
    """Validate API key against hash"""
    return hash_api_key(api_key) == hashed_key
