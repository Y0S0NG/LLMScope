"""Base client for LLMScope SDK"""
import requests
from typing import Optional


class BaseClient:
    """Base HTTP client for LLMScope API"""

    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        """
        Initialize LLMScope client

        Args:
            api_key: LLMScope API key
            base_url: LLMScope API base URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        timeout: int = 30
    ) -> dict:
        """
        Make HTTP request to LLMScope API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json: JSON request body
            params: Query parameters
            timeout: Request timeout in seconds

        Returns:
            Response JSON data

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(
            method=method,
            url=url,
            json=json,
            params=params,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()

    def _get(self, endpoint: str, params: Optional[dict] = None, **kwargs) -> dict:
        """Make GET request"""
        return self._request("GET", endpoint, params=params, **kwargs)

    def _post(self, endpoint: str, json: Optional[dict] = None, **kwargs) -> dict:
        """Make POST request"""
        return self._request("POST", endpoint, json=json, **kwargs)

    def _put(self, endpoint: str, json: Optional[dict] = None, **kwargs) -> dict:
        """Make PUT request"""
        return self._request("PUT", endpoint, json=json, **kwargs)

    def _delete(self, endpoint: str, **kwargs) -> dict:
        """Make DELETE request"""
        return self._request("DELETE", endpoint, **kwargs)