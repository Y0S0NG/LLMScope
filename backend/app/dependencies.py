"""Dependency injection"""
from fastapi import Depends, HTTPException, Header
from typing import Optional
from .config import settings


async def get_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Validate API key from header"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    # TODO: Validate against database
    return x_api_key


async def get_db():
    """Get database session"""
    # TODO: Implement database session
    pass
