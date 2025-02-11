"""Test configuration and fixtures."""

import json
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Dict, Optional, cast

import httpx
import pytest
import respx
from pydantic import BaseModel, HttpUrl

from anyrun import AnyRunClient
from anyrun.config import BaseConfig
from anyrun.types import CacheBackend, LogLevel, RateLimitBackend, RetryStrategy

# Constants for testing
TEST_API_KEY = "0123456789abcdef0123456789abcdef"
TEST_BASE_URL = "https://api.any.run"


class MockResponse(BaseModel):
    """Mock response model."""

    status_code: int = 200
    headers: Dict[str, str] = {}
    content: bytes = b"{}"

    def json(self) -> Dict[str, Any]:
        """Get JSON response."""
        return cast(Dict[str, Any], json.loads(self.content.decode()))


@pytest.fixture
def mock_api() -> respx.Router:
    """Mock API responses."""
    with respx.mock(base_url=TEST_BASE_URL, assert_all_called=False) as respx_mock:
        yield respx_mock


@pytest.fixture
def config() -> BaseConfig:
    """Get test configuration."""
    return BaseConfig(
        api_key=TEST_API_KEY,
        base_url=HttpUrl(TEST_BASE_URL),
        proxies=None,
        user_agent=None,
        cache_enabled=False,
        rate_limit_enabled=False,
        cache_backend=CacheBackend.MEMORY,
        rate_limit_backend=RateLimitBackend.MEMORY,
        retry_strategy=RetryStrategy.EXPONENTIAL,
        log_level=LogLevel.INFO,
    )


@pytest.fixture
async def client(config: BaseConfig) -> AsyncGenerator[AnyRunClient, None]:
    """Get test client."""
    client = AnyRunClient(
        api_key=config.api_key,
        base_url=config.base_url,
        cache_enabled=config.cache_enabled,
        rate_limit_enabled=config.rate_limit_enabled,
        cache_backend=config.cache_backend,
        rate_limit_backend=config.rate_limit_backend,
        retry_strategy=config.retry_strategy,
        log_level=config.log_level,
    )
    yield client
    await client.close()


@pytest.fixture
def fixtures_path() -> Path:
    """Get path to test fixtures."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def load_fixture() -> Callable[[str], Dict[str, Any]]:
    """Load test fixture."""

    def _load_fixture(name: str) -> Dict[str, Any]:
        path = Path(__file__).parent / "fixtures" / f"{name}.json"
        with open(path) as f:
            return cast(Dict[str, Any], json.load(f))

    return _load_fixture


@pytest.fixture
def mock_response() -> Callable[..., httpx.Response]:
    """Create mock response."""

    def _mock_response(
        *,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        headers = headers or {"Content-Type": "application/json"}
        content = content or {}
        return httpx.Response(
            status_code=status_code,
            headers=headers,
            content=json.dumps(content).encode(),
        )

    return _mock_response
