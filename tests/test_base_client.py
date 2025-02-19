"""Tests for base client functionality."""

import pytest
from httpx import AsyncClient, Response
from pydantic import HttpUrl

from anyrun.client import AnyRunClient, BaseClient
from anyrun.config import BaseConfig
from anyrun.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)


async def test_base_client_initialization(api_key: str) -> None:
    """Test base client initialization."""
    config = BaseConfig(
        api_key=api_key,
        base_url=HttpUrl("https://api.any.run"),
    )
    client = BaseClient(config)
    assert client.config == config
    assert client._client is None


async def test_anyrun_client_initialization(api_key: str) -> None:
    """Test ANY.RUN client initialization."""
    client = AnyRunClient(api_key=api_key)
    assert client.config.api_key == api_key
    assert client.sandbox is not None


@pytest.mark.parametrize(
    "status_code,error_class",
    [
        (401, AuthenticationError),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, ServerError),
        (418, APIError),  # Any other error
    ],
)
async def test_error_handling(
    mock_api: pytest.fixture,
    client: AnyRunClient,
    status_code: int,
    error_class: Exception,
) -> None:
    """Test error handling."""
    mock_api.get("https://api.any.run/test").mock(
        return_value=Response(status_code, json={"message": "Error"})
    )

    with pytest.raises(error_class):
        await client._base_client._request("GET", "/test")


async def test_rate_limiter(client: AnyRunClient) -> None:
    """Test rate limiter functionality."""
    assert client.rate_limiter is not None
    assert client.rate_limiter.rate == 1.0
    assert client.rate_limiter.burst == 10


async def test_cache(client: AnyRunClient) -> None:
    """Test cache functionality."""
    assert client.cache is not None
    assert client.cache.enabled is False  # Disabled in test fixture


async def test_client_context_manager(api_key: str, mock_api: pytest.fixture) -> None:
    """Test client context manager."""
    async with AnyRunClient(api_key=api_key) as client:
        # Make a request to initialize the client
        mock_api.get("https://api.any.run/test").mock(
            return_value=Response(200, json={"message": "OK"})
        )
        await client.test_request("/test")
        assert client._base_client._client is not None
    assert client._base_client._client is None
