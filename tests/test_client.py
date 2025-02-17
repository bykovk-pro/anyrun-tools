"""Tests for ANY.RUN API client."""

from typing import Any, Dict, Optional, Type, Tuple, cast

import httpx
import pytest
from _pytest.fixtures import FixtureRequest
import respx

from anyrun import AnyRunClient
from anyrun.config import BaseConfig
from anyrun.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from anyrun.types import CacheBackend


@pytest.mark.asyncio
async def test_client_initialization(config: BaseConfig) -> None:
    """Test client initialization."""
    async with AnyRunClient(
        api_key=config.api_key,
        base_url=config.base_url,
        cache_enabled=config.cache_enabled,
        rate_limit_enabled=config.rate_limit_enabled,
    ) as client:
        assert client.config.api_key == config.api_key
        assert str(client.config.base_url) == str(config.base_url)


@pytest.mark.asyncio
async def test_client_context_manager(config: BaseConfig) -> None:
    """Test client context manager."""
    client = AnyRunClient(
        api_key=config.api_key,
        base_url=config.base_url,
        retry_enabled=False,
    )

    try:
        async with client as c:
            with pytest.raises(NotFoundError):
                await c.test_request("/test")
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_client_properties(config: BaseConfig) -> None:
    """Test client properties."""
    async with AnyRunClient(
        api_key=config.api_key,
        base_url=config.base_url,
        cache_enabled=True,
        rate_limit_enabled=True,
    ) as client:
        assert client.cache is not None
        assert client.rate_limiter is not None
        assert client.sandbox is not None
        assert client.ti_lookup is not None
        assert client.ti_yara is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code,error_class",
    [
        (401, AuthenticationError),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, ServerError),
        (400, APIError),
    ],
)
async def test_client_error_handling(
    mock_api: respx.Router,
    config: BaseConfig,
    status_code: int,
    error_class: Type[APIError],
) -> None:
    """Test client error handling."""
    mock_api.get("/test").mock(
        return_value=httpx.Response(
            status_code=status_code,
            json={"error": True, "message": "Test error"},
            headers={"Retry-After": "1"} if status_code == 429 else {},
        )
    )

    async with AnyRunClient(
        api_key=config.api_key,
        base_url=config.base_url,
        retry_enabled=False,
        rate_limit_enabled=False,
    ) as client:
        with pytest.raises(error_class):
            await client.test_request("/test")


@pytest.mark.asyncio
async def test_client_retry(mock_api: respx.Router, config: BaseConfig) -> None:
    """Test client retry mechanism."""
    mock_api.get("/test").mock(
        side_effect=[
            httpx.Response(status_code=500),
            httpx.Response(status_code=500),
            httpx.Response(status_code=200, json={"error": False, "data": {}}),
        ]
    )

    async with AnyRunClient(
        api_key=config.api_key,
        base_url=config.base_url,
        retry_enabled=True,
        retry_max_attempts=3,
    ) as client:
        response = await client.test_request("/test")
        assert response["error"] is False


@pytest.mark.asyncio
async def test_client_rate_limit(
    mock_api: respx.Router, config: BaseConfig
) -> None:
    """Test client rate limiting."""
    mock_api.get("/test").mock(
        return_value=httpx.Response(
            status_code=429,
            headers={"Retry-After": "1"},
            json={"error": True, "message": "Rate limit exceeded"},
        )
    )

    async with AnyRunClient(
        api_key=config.api_key,
        base_url=config.base_url,
        rate_limit_enabled=True,
        retry_enabled=False,
    ) as client:
        with pytest.raises(RateLimitError) as exc_info:
            await client.test_request("/test")
        assert exc_info.value.retry_after == 1


@pytest.mark.asyncio
async def test_client_caching(mock_api: respx.Router, config: BaseConfig) -> None:
    """Test client caching."""
    mock_api.get("/test").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"error": False, "data": {"test": "value"}},
        )
    )

    async with AnyRunClient(
        api_key=config.api_key,
        base_url=config.base_url,
        cache_enabled=True,
        cache_backend=CacheBackend.MEMORY,
    ) as client:
        # First request should hit the API
        response1 = await client.test_request("/test")
        assert response1["error"] is False

        # Second request should hit the cache
        response2 = await client.test_request("/test")
        assert response2["error"] is False
        assert response2 == response1


@pytest.mark.asyncio
async def test_client_headers(mock_api: respx.Router, config: BaseConfig) -> None:
    """Test client headers."""
    mock_api.get("/test").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"error": False, "data": {}},
        )
    )

    async with AnyRunClient(
        api_key=config.api_key,
        base_url=config.base_url,
        headers={"X-Test": "test"},
    ) as client:
        response = await client.test_request("/test")
        assert response["error"] is False


@pytest.mark.asyncio
async def test_client_close(config: BaseConfig) -> None:
    """Test client close."""
    client = AnyRunClient(
        api_key=config.api_key,
        base_url=config.base_url,
        retry_enabled=False,
        rate_limit_enabled=False,
    )
    await client.close()
    # Test that client is closed by trying to make a request
    with pytest.raises(APIError):
        await client.test_request("/test")
