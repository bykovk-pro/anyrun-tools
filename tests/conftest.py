"""Common test fixtures and configuration."""

import os
from typing import AsyncGenerator, Generator

import pytest
import respx
from httpx import AsyncClient

from anyrun import AnyRunClient
from anyrun.sandbox.v1.client import SandboxClientV1


@pytest.fixture
def api_key() -> str:
    """Get API key for tests."""
    return "test_api_key"


@pytest.fixture
def mock_api() -> Generator[respx.Router, None, None]:
    """Mock API responses."""
    with respx.mock(assert_all_called=False) as respx_mock:
        yield respx_mock


@pytest.fixture
async def client(api_key: str) -> AsyncGenerator[AnyRunClient, None]:
    """Get test client instance."""
    async with AnyRunClient(
        api_key=api_key,
        sandbox_version="v1",
        cache_enabled=False,
        timeout=1.0,  # Short timeout for tests
    ) as client:
        yield client


@pytest.fixture
async def sandbox_client(api_key: str) -> AsyncGenerator[SandboxClientV1, None]:
    """Get test sandbox client instance."""
    client = SandboxClientV1(
        api_key=api_key,
        timeout=1.0,  # Short timeout for tests
    )
    yield client
    await client.close()
