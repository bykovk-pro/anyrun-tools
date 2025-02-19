"""Base client for ANY.RUN APIs."""

from typing import Any, Dict, Optional, Union, cast

import httpx
from loguru import logger
from pydantic import HttpUrl
from redis.asyncio import Redis as AsyncRedis

from .config import BaseConfig
from .constants import (
    API_BASE_URL,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    HEADER_API_KEY,
    HEADER_USER_AGENT,
)
from .exceptions import APIError, AuthenticationError, NotFoundError, RateLimitError, ServerError
from .sandbox import create_sandbox_client
from .ti_lookup import TILookupClient
from .ti_yara import TIYaraClient
from .types import CacheBackend, RetryStrategy
from .utils import Cache, RateLimiter, retry
from .utils.cache import CacheBackend as CacheBackendType
from .utils.cache import MemoryCache


class BaseClient:
    """Base client for ANY.RUN APIs."""

    def __init__(self, config: BaseConfig, client: Optional[httpx.AsyncClient] = None) -> None:
        """Initialize base client.

        Args:
            config: Client configuration
            client: Optional pre-configured HTTP client
        """
        self.config = config
        self._client = client
        self._cache: Optional[Cache] = None
        self._rate_limiter: Optional[RateLimiter] = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized.

        Returns:
            httpx.AsyncClient: HTTP client instance
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=str(self.config.base_url),
                timeout=self.config.timeout,
                headers=self._get_default_headers(),
                verify=self.config.verify_ssl,
                follow_redirects=True,
            )
        return self._client

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers.

        Returns:
            Dict[str, str]: Default headers
        """
        headers = {
            HEADER_USER_AGENT: self.config.user_agent or DEFAULT_USER_AGENT,
            HEADER_API_KEY: self.config.api_key,
            "Accept": "application/json",
        }
        headers.update(self.config.headers)
        return headers

    @property
    def cache(self) -> Cache:
        """Get cache instance.

        Returns:
            Cache: Cache instance
        """
        if self._cache is None:
            backend: Union[CacheBackendType, AsyncRedis[Any], None] = None
            if self.config.cache_backend == CacheBackend.REDIS:
                backend = AsyncRedis()
            elif self.config.cache_backend == CacheBackend.MEMORY:
                backend = MemoryCache()

            self._cache = Cache(
                backend=backend,
                enabled=self.config.cache_enabled,
                prefix=f"anyrun:{self.config.api_version}:",
                default_ttl=self.config.cache_ttl,
            )
        return self._cache

    @property
    def rate_limiter(self) -> RateLimiter:
        """Get rate limiter instance.

        Returns:
            RateLimiter: Rate limiter instance
        """
        if self._rate_limiter is None:
            self._rate_limiter = RateLimiter(
                rate=1.0,  # Will be set per endpoint
                burst=10,
                key=f"anyrun:{self.config.api_version}",
            )
        return self._rate_limiter

    async def _request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cache_key: Optional[str] = None,
        cache_ttl: Optional[int] = None,
        rate_limit: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request without retry.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            json: JSON body
            data: Form data
            files: Files to upload
            headers: Additional headers
            cache_key: Cache key
            cache_ttl: Cache TTL in seconds
            rate_limit: Rate limit in requests per second

        Returns:
            Dict[str, Any]: Response data

        Raises:
            APIError: If request fails
        """
        # Check cache
        if cache_key and method.upper() == "GET":
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cast(Dict[str, Any], cached)

        # Apply rate limiting
        if rate_limit and self.config.rate_limit_enabled:
            self.rate_limiter.rate = rate_limit
            if self.config.retry_strategy == RetryStrategy.EXPONENTIAL:
                await self.rate_limiter.acquire()
            elif not await self.rate_limiter.check():
                raise RateLimitError(
                    message="Rate limit exceeded",
                    retry_after=int(1.0 / rate_limit),
                )

        # Make request
        client = await self._ensure_client()
        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=headers,
            )
            response.raise_for_status()
            response_data: Dict[str, Any] = response.json()

            # Cache successful GET response
            if cache_key and method.upper() == "GET":
                await self.cache.set(cache_key, response_data, ttl=cache_ttl)

            return response_data

        except httpx.HTTPStatusError as e:
            error_msg = str(e)
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict):
                    error_msg = error_data.get("message", str(e))
            except Exception:
                # Failed to parse error response, use original error message
                logger.debug("Failed to parse error response JSON")

            if e.response.status_code == 401:
                raise AuthenticationError(error_msg) from e
            elif e.response.status_code == 404:
                raise NotFoundError(error_msg) from e
            elif e.response.status_code == 429:
                raise RateLimitError(
                    message=error_msg,
                    retry_after=int(float(e.response.headers.get("Retry-After", "60"))),
                )
            elif e.response.status_code >= 500:
                raise ServerError(error_msg)
            else:
                raise APIError(error_msg) from e

        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")

    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cache_key: Optional[str] = None,
        cache_ttl: Optional[int] = None,
        rate_limit: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            json: JSON body
            data: Form data
            files: Files to upload
            headers: Additional headers
            cache_key: Cache key
            cache_ttl: Cache TTL in seconds
            rate_limit: Rate limit in requests per second

        Returns:
            Dict[str, Any]: Response data

        Raises:
            APIError: If request fails
        """

        async def _request_with_config(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            return await self._request(*args, **kwargs)

        _request_with_config.config = self.config  # type: ignore

        retry_decorator = retry(
            max_attempts=self.config.retry_max_attempts,
            delay=self.config.retry_initial_delay,
            max_delay=self.config.retry_max_delay,
            exponential=self.config.retry_strategy == RetryStrategy.EXPONENTIAL,
            jitter=True,
        )

        return await retry_decorator(_request_with_config)(
            method=method,
            url=url,
            params=params,
            json=json,
            data=data,
            files=files,
            headers=headers,
            cache_key=cache_key,
            cache_ttl=cache_ttl,
            rate_limit=rate_limit,
        )

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "BaseClient":
        """Enter async context."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context."""
        await self.close()

    async def test_request(self, url: str) -> Dict[str, Any]:
        """Make test request.

        Args:
            url: Request URL

        Returns:
            Dict[str, Any]: Response data

        Raises:
            APIError: If request fails
        """
        return await self._request("GET", url)


class AnyRunClient:
    """Main client for ANY.RUN APIs."""

    def __init__(
        self,
        api_key: str,
        sandbox_version: str = "v1",
        ti_lookup_version: str = "v1",
        ti_yara_version: str = "v1",
        **kwargs: Any,
    ) -> None:
        """Initialize ANY.RUN client.

        Args:
            api_key: ANY.RUN API key
            sandbox_version: Sandbox API version
            ti_lookup_version: TI Lookup API version
            ti_yara_version: TI YARA API version
            **kwargs: Additional configuration options
        """
        self.config = BaseConfig(
            api_key=api_key,
            base_url=HttpUrl(API_BASE_URL),
            timeout=kwargs.get("timeout", DEFAULT_TIMEOUT),
            user_agent=kwargs.get("user_agent", DEFAULT_USER_AGENT),
            verify_ssl=kwargs.get("verify_ssl", True),
            headers=kwargs.get("headers", {}),
            cache_enabled=kwargs.get("cache_enabled", True),
            cache_ttl=kwargs.get("cache_ttl", 300),
            cache_backend=kwargs.get("cache_backend", CacheBackend.MEMORY),
            rate_limit_enabled=kwargs.get("rate_limit_enabled", True),
            retry_strategy=kwargs.get("retry_strategy", RetryStrategy.EXPONENTIAL),
        )

        self._base_client = BaseClient(self.config)

        # Initialize API clients
        self.sandbox = create_sandbox_client(
            api_key=api_key,
            version=sandbox_version,
            base_url=self.config.base_url,
            timeout=int(self.config.timeout),
            verify_ssl=self.config.verify_ssl,
            user_agent=self.config.user_agent,
            headers=self.config.headers,
        )
        self.ti_lookup = TILookupClient(
            api_key=api_key,
            version=ti_lookup_version,
            cache_enabled=self.config.cache_enabled,
            timeout=int(self.config.timeout),
        )
        self.ti_yara = TIYaraClient(
            api_key=api_key,
            version=ti_yara_version,
            cache_enabled=self.config.cache_enabled,
            timeout=int(self.config.timeout),
        )

    @property
    def cache(self) -> Cache:
        """Get cache instance.

        Returns:
            Cache: Cache instance
        """
        return self._base_client.cache

    @property
    def rate_limiter(self) -> RateLimiter:
        """Get rate limiter instance.

        Returns:
            RateLimiter: Rate limiter instance
        """
        return self._base_client.rate_limiter

    async def test_request(self, url: str) -> Dict[str, Any]:
        """Make test request.

        Args:
            url: Request URL

        Returns:
            Dict[str, Any]: Response data

        Raises:
            APIError: If request fails
        """
        return await self._base_client.request("GET", url)

    async def close(self) -> None:
        """Close all clients."""
        await self.sandbox.close()
        await self.ti_lookup.close()
        await self.ti_yara.close()
        await self._base_client.close()

    async def __aenter__(self) -> "AnyRunClient":
        """Enter async context."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context."""
        await self.close()
