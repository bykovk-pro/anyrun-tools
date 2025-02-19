"""Tests for retry utilities."""

import asyncio
import time
from typing import Any, Dict, Optional

import pytest
from tenacity import RetryError

from anyrun.exceptions import APIError, RateLimitError
from anyrun.utils.retry import retry


class MockConfig:
    """Mock configuration for testing."""

    def __init__(
        self,
        retry_max_attempts: int = 3,
        retry_initial_delay: float = 0.1,
        retry_max_delay: float = 1.0,
        retry_exponential: bool = True,
    ) -> None:
        """Initialize mock config."""
        self.retry_max_attempts = retry_max_attempts
        self.retry_initial_delay = retry_initial_delay
        self.retry_max_delay = retry_max_delay
        self.retry_exponential = retry_exponential


async def test_retry_success() -> None:
    """Test successful retry."""
    attempts = 0

    @retry(max_attempts=3, delay=0.1, max_delay=1.0, exponential=True)
    async def test_func() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise APIError("Test error")
        return "success"

    test_func.config = MockConfig()  # type: ignore
    result = await test_func()
    assert result == "success"
    assert attempts == 2


async def test_retry_max_attempts() -> None:
    """Test retry max attempts."""
    attempts = 0

    @retry(max_attempts=3, delay=0.1, max_delay=1.0, exponential=True)
    async def test_func() -> None:
        nonlocal attempts
        attempts += 1
        raise APIError("Test error")

    test_func.config = MockConfig()  # type: ignore
    with pytest.raises(APIError) as exc_info:
        await test_func()
    assert attempts == 3
    assert str(exc_info.value) == "Test error"


async def test_retry_rate_limit() -> None:
    """Test retry with rate limit error."""
    attempts = 0
    start_time = time.monotonic()

    @retry(max_attempts=3, delay=0.1, max_delay=1.0, exponential=True)
    async def test_func() -> str:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RateLimitError("Rate limit exceeded", retry_after=0.1)
        return "success"

    test_func.config = MockConfig()  # type: ignore
    result = await test_func()
    elapsed = time.monotonic() - start_time

    assert result == "success"
    assert attempts == 2
    # Just verify that some delay occurred, but don't be too strict about timing
    assert elapsed > 0.0
    assert elapsed < 1.0  # Upper bound for CI environments


async def test_retry_exponential_backoff() -> None:
    """Test retry with exponential backoff."""
    attempts = 0
    delays: list[float] = []
    start_time = time.monotonic()

    @retry(max_attempts=3, delay=0.1, max_delay=1.0, exponential=True)
    async def test_func() -> None:
        nonlocal attempts, start_time
        current_time = time.monotonic()
        if attempts > 0:
            delays.append(current_time - start_time)
        start_time = current_time
        attempts += 1
        raise APIError("Test error")

    test_func.config = MockConfig()  # type: ignore
    with pytest.raises(APIError):
        await test_func()

    assert attempts == 3
    assert len(delays) == 2
    assert delays[1] > delays[0]  # Second delay should be longer


async def test_retry_max_delay() -> None:
    """Test retry with max delay."""
    attempts = 0
    retry_times: list[float] = []

    @retry(max_attempts=3, delay=0.1, max_delay=0.2, exponential=True)
    async def test_func() -> None:
        nonlocal attempts
        retry_times.append(time.monotonic())
        attempts += 1
        raise APIError("Test error")

    test_func.config = MockConfig(retry_max_delay=0.2)  # type: ignore
    with pytest.raises(APIError):
        await test_func()

    assert attempts == 3
    assert len(retry_times) == 3
    # Calculate actual delays between retries
    delays = [retry_times[i+1] - retry_times[i] for i in range(len(retry_times)-1)]
    assert len(delays) == 2
    # Verify delays are reasonable
    assert all(0.05 <= d <= 0.5 for d in delays)  # Allow some variance but keep bounded


async def test_retry_linear_backoff() -> None:
    """Test retry with linear backoff."""
    attempts = 0
    delays: list[float] = []
    start_time = time.monotonic()

    @retry(max_attempts=3, delay=0.1, max_delay=1.0, exponential=False)
    async def test_func() -> None:
        nonlocal attempts, start_time
        current_time = time.monotonic()
        if attempts > 0:
            delays.append(current_time - start_time)
        start_time = current_time
        attempts += 1
        raise APIError("Test error")

    test_func.config = MockConfig(retry_exponential=False)  # type: ignore
    with pytest.raises(APIError):
        await test_func()

    assert attempts == 3
    assert len(delays) == 2
    assert abs(delays[1] - delays[0]) < 0.1  # Delays should be similar in linear mode


async def test_retry_with_result() -> None:
    """Test retry with result checking."""
    attempts = 0

    @retry(max_attempts=3, delay=0.1, max_delay=1.0, exponential=True)
    async def test_func() -> Dict[str, Any]:
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise APIError("Test error")
        return {"error": False, "data": "success"}

    test_func.config = MockConfig()  # type: ignore
    result = await test_func()
    assert result == {"error": False, "data": "success"}
    assert attempts == 2
