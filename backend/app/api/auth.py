"""Authentication endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class APIKeyCreate(BaseModel):
    """API key creation request"""
    name: str
    description: str = ""


@router.post("/api-keys")
async def create_api_key(key_data: APIKeyCreate):
    """Create new API key"""
    # TODO: Implement API key generation
    return {
        "api_key": "llmscope_placeholder_key",
        "name": key_data.name,
        "created_at": "2025-10-04T00:00:00Z"
    }


@router.get("/api-keys")
async def list_api_keys():
    """List all API keys (masked)"""
    # TODO: Implement API key listing
    return {"keys": []}
