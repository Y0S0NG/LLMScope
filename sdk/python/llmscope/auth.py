"""Auth API module"""
from typing import List, Union
from .client import BaseClient
from .models import APIKeyCreate


class AuthClient(BaseClient):
    """Client for LLMScope Auth API"""

    def list_api_keys(self) -> List[dict]:
        """
        List all API keys (masked)

        Returns:
            List of API keys with masked values

        Example:
            ```python
            keys = client.auth.list_api_keys()
            for key in keys:
                print(f"{key['name']}: {key['key_masked']}")
            ```
        """
        return self._get("/api/v1/auth/api-keys")

    def create_api_key(self, key: Union[APIKeyCreate, dict]) -> dict:
        """
        Create new API key

        Args:
            key: API key configuration as APIKeyCreate object or dict

        Returns:
            Created API key with full key value (only shown once!)

        Example:
            ```python
            from llmscope.models import APIKeyCreate

            # Create API key
            key = APIKeyCreate(
                name="Production API Key",
                description="API key for production environment"
            )

            created_key = client.auth.create_api_key(key)
            print(f"API Key: {created_key['key']}")
            print("Save this key - it won't be shown again!")
            ```

            ```python
            # Or use a dict
            key = {
                "name": "Development Key",
                "description": "For local development"
            }

            created_key = client.auth.create_api_key(key)
            ```
        """
        if isinstance(key, APIKeyCreate):
            key_data = key.model_dump(exclude_none=True)
        else:
            key_data = key

        return self._post("/api/v1/auth/api-keys", json=key_data)