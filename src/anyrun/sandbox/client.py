"""Sandbox API client implementation."""

import json
import os
from typing import Any, AsyncGenerator, Dict, Optional, Union, cast

import httpx
from loguru import logger
from pydantic import HttpUrl

from ..exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .v1.models.analysis import (
    AddTimeResponse,
    AnalysisListRequest,
    AnalysisListResponse,
    AnalysisRequest,
    AnalysisResponse,
    DeleteAnalysisResponse,
    ObjectType,
    StopAnalysisResponse,
)
from .v1.models.environment import EnvironmentResponse


class SandboxClient:
    """Sandbox API client."""

    def __init__(
        self,
        api_key: str,
        version: str = "v1",
        base_url: Optional[HttpUrl] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        proxies: Optional[Dict[str, str]] = None,
        user_agent: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        cache_enabled: bool = True,
        cache_backend: str = "memory",
        cache_ttl: int = 300,
        rate_limit_enabled: bool = True,
        rate_limit_backend: str = "memory",
    ) -> None:
        """Initialize Sandbox client.

        Args:
            api_key: ANY.RUN API key
            version: API version
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
            proxies: Proxy configuration
            user_agent: User agent string
            headers: Additional headers
            cache_enabled: Enable caching
            cache_backend: Cache backend type
            cache_ttl: Cache TTL in seconds
            rate_limit_enabled: Enable rate limiting
            rate_limit_backend: Rate limit backend type
        """
        self.api_key = api_key
        self.version = version
        self.base_url = str(base_url or "https://api.any.run").rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.proxies = proxies
        self.user_agent = user_agent
        self.headers = headers or {}
        self.cache_enabled = cache_enabled
        self.cache_backend = cache_backend
        self.cache_ttl = cache_ttl
        self.rate_limit_enabled = rate_limit_enabled
        self.rate_limit_backend = rate_limit_backend
        self._client: Optional[httpx.AsyncClient] = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure client is initialized.

        Returns:
            httpx.AsyncClient: HTTP client

        Raises:
            ConfigurationError: If client is not initialized
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

    def _get_endpoint(self, path: str) -> str:
        """Get versioned API endpoint.

        Args:
            path: API path

        Returns:
            str: Full API endpoint with version
        """
        path = path.lstrip("/")
        return f"/{self.version}/{path}"

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response.

        Args:
            response: HTTP response

        Returns:
            Dict[str, Any]: Response data

        Raises:
            AuthenticationError: If authentication failed
            NotFoundError: If resource not found
            RateLimitError: If rate limit exceeded
            ServerError: If server error occurred
            APIError: If other API error occurred
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise APIError(f"Invalid JSON response: {response.text}")

        if response.status_code == 200:
            return cast(Dict[str, Any], data)

        error_message = data.get("message", "Unknown error")

        if response.status_code == 401:
            raise AuthenticationError(error_message, response.status_code)
        elif response.status_code == 404:
            raise NotFoundError(error_message, response.status_code)
        elif response.status_code == 429:
            raise RateLimitError(error_message, response.status_code)
        elif response.status_code >= 500:
            raise ServerError(error_message, response.status_code)
        else:
            raise APIError(error_message, response.status_code)

    def _get_file_content(self, file: Union[str, bytes]) -> bytes:
        """Get file content as bytes.

        Args:
            file: File content as string or bytes

        Returns:
            bytes: File content as bytes

        Raises:
            ValidationError: If file content is invalid
        """
        if isinstance(file, str):
            if os.path.isfile(file):
                with open(file, "rb") as f:
                    return f.read()
            return file.encode()
        return file

    async def analyze(self, **kwargs: Any) -> AnalysisResponse:
        """Submit new analysis.

        Args:
            **kwargs: Analysis parameters (see AnalysisRequest schema)

        Returns:
            AnalysisResponse: Analysis response

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request failed
        """
        try:
            request = AnalysisRequest(**kwargs)
            data = request.model_dump(exclude_unset=True)

            # Convert enum values to strings
            for key, value in data.items():
                if hasattr(value, "value"):
                    data[key] = value.value

            files = None
            if request.obj_type == ObjectType.FILE:
                if not request.file:
                    raise ValidationError("file is required for file analysis")
                # Handle file content as bytes
                filename = kwargs.get("filename", "malware.exe")
                file_content = self._get_file_content(request.file)
                files = {
                    "file": (
                        filename,
                        file_content,
                    )
                }

            client = await self._ensure_client()
            response = await client.post(
                self._get_endpoint("/analysis"),
                headers=self._get_headers(),
                data=data,
                files=files,
            )

            result = await self._handle_response(response)
            return AnalysisResponse.model_validate(result)

        except ValidationError as e:
            raise ValidationError(f"Invalid analysis parameters: {str(e)}")
        except Exception as e:
            raise APIError(f"Failed to submit analysis: {str(e)}")

    async def get_analysis(self, task_id: str) -> AnalysisResponse:
        """Get analysis information.

        Args:
            task_id: Analysis task ID

        Returns:
            AnalysisResponse: Analysis information

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.get(
            self._get_endpoint(f"/analysis/{task_id}"),
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return AnalysisResponse.model_validate(result)

    async def list_analyses(self, **kwargs: Any) -> AnalysisListResponse:
        """Get list of analyses.

        Args:
            **kwargs: List parameters (see AnalysisListRequest schema)

        Returns:
            AnalysisListResponse: List of analyses

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request failed
        """
        try:
            request = AnalysisListRequest(**kwargs)
            client = await self._ensure_client()
            response = await client.get(
                self._get_endpoint("/analysis"),
                headers=self._get_headers(),
                params=request.model_dump(exclude_unset=True),
            )

            result = await self._handle_response(response)
            return AnalysisListResponse.model_validate(result)

        except ValidationError as e:
            raise ValidationError(f"Invalid list parameters: {str(e)}")
        except Exception as e:
            raise APIError(f"Failed to list analyses: {str(e)}")

    async def get_analysis_status(self, task_id: str) -> AnalysisResponse:
        """Get analysis status.

        Args:
            task_id: Analysis task ID

        Returns:
            AnalysisResponse: Status information

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.get(
            self._get_endpoint(f"/analysis/{task_id}/status"),
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return AnalysisResponse.model_validate(result)

    async def get_analysis_monitor(self, task_id: str) -> AnalysisResponse:
        """Get analysis monitor data.

        Args:
            task_id: Analysis task ID

        Returns:
            AnalysisResponse: Monitor data

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.get(
            self._get_endpoint(f"/analysis/{task_id}/monitor"),
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return AnalysisResponse.model_validate(result)

    async def get_analysis_status_stream(
        self, task_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Get real-time analysis status updates using SSE.

        Args:
            task_id: Analysis task ID

        Yields:
            Dict[str, Any]: Status update

        Raises:
            APIError: If API request failed
        """
        timeout = httpx.Timeout(timeout=None)  # No timeout for SSE
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "GET",
                f"{self.base_url}/analysis/status/{task_id}/stream",
                headers=self._get_headers(),
            ) as response:
                if response.status_code != 200:
                    raise APIError(f"Failed to connect to SSE: {response.status_code}")

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue

                    if line.startswith("data:"):
                        try:
                            data = json.loads(line[5:].strip())
                            yield cast(Dict[str, Any], data)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse SSE data: {e}")
                            continue

    async def get_analysis_monitor_stream(
        self, task_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Get real-time analysis monitor updates using SSE.

        Args:
            task_id: Analysis task ID

        Yields:
            Dict[str, Any]: Monitor update

        Raises:
            APIError: If API request failed
        """
        timeout = httpx.Timeout(timeout=None)  # No timeout for SSE
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "GET",
                f"{self.base_url}/analysis/monitor/{task_id}/stream",
                headers=self._get_headers(),
            ) as response:
                if response.status_code != 200:
                    raise APIError(f"Failed to connect to SSE: {response.status_code}")

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue

                    if line.startswith("data:"):
                        try:
                            data = json.loads(line[5:].strip())
                            yield cast(Dict[str, Any], data)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse SSE data: {e}")
                            continue

    async def add_analysis_time(self, task_id: str) -> AddTimeResponse:
        """Add time to running analysis.

        Args:
            task_id: Analysis task ID

        Returns:
            AddTimeResponse: Response data

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.post(
            f"/analysis/{task_id}/time",
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return AddTimeResponse.model_validate(result)

    async def stop_analysis(self, task_id: str) -> StopAnalysisResponse:
        """Stop running analysis.

        Args:
            task_id: Analysis task ID

        Returns:
            StopAnalysisResponse: Response data

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.post(
            f"/analysis/{task_id}/stop",
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return StopAnalysisResponse.model_validate(result)

    async def delete_analysis(self, task_id: str) -> DeleteAnalysisResponse:
        """Delete analysis.

        Args:
            task_id: Analysis task ID

        Returns:
            DeleteAnalysisResponse: Response data

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.delete(
            f"/analysis/{task_id}",
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return DeleteAnalysisResponse.model_validate(result)

    async def get_environment(self) -> EnvironmentResponse:
        """Get available environment information.

        Returns:
            EnvironmentResponse: Environment information

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.get(
            self._get_endpoint("/environment"),
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return EnvironmentResponse.model_validate(result)

    async def analyze_file(
        self, file: Union[str, bytes], **kwargs: Any
    ) -> AnalysisResponse:
        """Submit file for analysis.

        Args:
            file: File content as string or bytes
            **kwargs: Additional analysis parameters

        Returns:
            AnalysisResponse: Analysis response

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request failed
        """
        kwargs["obj_type"] = ObjectType.FILE
        kwargs["file"] = file
        return await self.analyze(**kwargs)

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "SandboxClient":
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
