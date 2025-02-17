"""Base class for sandbox API clients."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Union, Generic

import httpx
from loguru import logger
from pydantic import HttpUrl, BaseModel

from ..exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)

TAnalysisResponse = TypeVar("TAnalysisResponse", bound=BaseModel)
TAnalysisListResponse = TypeVar("TAnalysisListResponse", bound=BaseModel)
TEnvironmentResponse = TypeVar("TEnvironmentResponse", bound=BaseModel)


class BaseSandboxClient(Generic[TAnalysisResponse, TAnalysisListResponse, TEnvironmentResponse], ABC):
    """Base class for sandbox API clients."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[HttpUrl] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        proxies: Optional[Dict[str, str]] = None,
        user_agent: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize base sandbox client.

        Args:
            api_key: ANY.RUN API key
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
            proxies: Proxy configuration
            user_agent: User agent string
            headers: Additional headers
        """
        self.api_key = api_key
        self.base_url = str(base_url or "https://api.any.run").rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.proxies = proxies
        self.user_agent = user_agent
        self.headers = headers or {}
        self._client: Optional[httpx.AsyncClient] = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure client is initialized.

        Returns:
            httpx.AsyncClient: HTTP client
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                follow_redirects=True,
                verify=self.verify_ssl,
                headers=self.headers,
            )
        return self._client

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization.

        Returns:
            Dict[str, str]: Headers dictionary
        """
        return {"Authorization": f"API-Key {self.api_key}"}

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response.

        Args:
            response: HTTP response

        Returns:
            Dict[str, Any]: Response data

        Raises:
            AuthenticationError: If authentication failed (401)
            NotFoundError: If resource not found (404)
            RateLimitError: If rate limit exceeded (429)
            ServerError: If server error occurred (5xx)
            APIError: If other API error occurred
        """
        try:
            data = response.json()
            if not isinstance(data, dict):
                raise APIError("Response data is not a dictionary")
        except json.JSONDecodeError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if response.status_code in (200, 201, 202):
            return data
        elif response.status_code == 401:
            raise AuthenticationError("Authentication failed", response.status_code)
        elif response.status_code == 404:
            raise NotFoundError("Resource not found", response.status_code)
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded", response.status_code)
        elif response.status_code >= 500:
            raise ServerError("Server error", response.status_code)
        else:
            raise APIError(f"API error: {response.status_code}", response.status_code)

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "BaseSandboxClient":
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context."""
        await self.close()

    @abstractmethod
    async def analyze_file(
        self, file: Union[str, bytes], **kwargs: Any
    ) -> TAnalysisResponse:
        """Submit file for analysis.

        Args:
            file: File content as string or bytes
            **kwargs: Additional analysis parameters

        Returns:
            TAnalysisResponse: Analysis response

        Raises:
            NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError

    @abstractmethod
    async def get_analysis(self, task_id: str) -> TAnalysisResponse:
        """Get analysis information.

        Args:
            task_id: Analysis task ID

        Returns:
            TAnalysisResponse: Analysis information

        Raises:
            NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError

    @abstractmethod
    async def list_analyses(self, **kwargs: Any) -> TAnalysisListResponse:
        """Get list of analyses.

        Args:
            **kwargs: List parameters

        Returns:
            TAnalysisListResponse: List of analyses

        Raises:
            NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError

    @abstractmethod
    async def get_analysis_monitor(self, task_id: str) -> Dict[str, Any]:
        """Get analysis monitor data.

        Args:
            task_id: Analysis task ID

        Returns:
            Dict[str, Any]: Monitor data

        Raises:
            NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError

    @abstractmethod
    async def get_environment(self) -> TEnvironmentResponse:
        """Get available environment information.

        Returns:
            TEnvironmentResponse: Environment information

        Raises:
            NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError
