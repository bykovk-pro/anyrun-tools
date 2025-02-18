"""Base sandbox client."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar

import httpx
from pydantic import HttpUrl

from ..config import BaseConfig
from ..constants import API_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_USER_AGENT
from ..exceptions import APIError, AuthenticationError, NotFoundError, RateLimitError, ServerError

A = TypeVar("A")  # Analysis response type
L = TypeVar("L")  # List response type
E = TypeVar("E")  # Environment response type


class BaseSandboxClient(Generic[A, L, E], ABC):
    """Base class for sandbox API clients."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[HttpUrl] = None,
        timeout: Optional[int] = None,
        verify_ssl: bool = True,
        user_agent: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize sandbox client.

        Args:
            api_key: ANY.RUN API key
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
            user_agent: User agent string
            headers: Additional headers
        """
        self.config = BaseConfig(
            api_key=api_key,
            base_url=base_url or HttpUrl(API_BASE_URL),
            timeout=timeout or DEFAULT_TIMEOUT,
            verify_ssl=verify_ssl,
            user_agent=user_agent or DEFAULT_USER_AGENT,
            headers=headers or {},
        )
        self._client: Optional[httpx.AsyncClient] = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure client is initialized.

        Returns:
            httpx.AsyncClient: HTTP client
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=str(self.config.base_url),
                timeout=self.config.timeout,
                follow_redirects=True,
                verify=self.config.verify_ssl,
                headers=self.config.headers,
            )
        return self._client

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization.

        Returns:
            Dict[str, str]: Headers dictionary
        """
        return {"Authorization": f"API-Key {self.config.api_key}"}

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

    async def __aenter__(self) -> "BaseSandboxClient[A, L, E]":
        """Enter async context."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context."""
        await self.close()

    @abstractmethod
    async def analyze_file(self, file: bytes, **kwargs: Any) -> A:
        """Submit file for analysis.

        Args:
            file: File content
            **kwargs: Additional analysis parameters

        Returns:
            A: Analysis response

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request failed
        """
        pass

    @abstractmethod
    async def get_analysis(self, task_id: str) -> A:
        """Get analysis information.

        Args:
            task_id: Analysis task ID

        Returns:
            A: Analysis information

        Raises:
            APIError: If API request failed
        """
        pass

    @abstractmethod
    async def list_analyses(self, **kwargs: Any) -> L:
        """Get list of analyses.

        Args:
            **kwargs: List parameters

        Returns:
            L: List of analyses

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request failed
        """
        pass

    @abstractmethod
    async def get_environment(self) -> E:
        """Get available environment information.

        Returns:
            E: Environment information

        Raises:
            APIError: If API request failed
        """
        pass

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
