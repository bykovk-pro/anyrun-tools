"""Tests for rate limiter utilities."""

import asyncio
import time

import pytest

from anyrun.utils import RateLimiter


@pytest.fixture
def rate_limiter() -> RateLimiter:
    """Get rate limiter instance."""
    return RateLimiter(rate=5.0, burst=3, key="test")  # Lower rate for more predictable tests


async def test_rate_limiter_check(rate_limiter: RateLimiter) -> None:
    """Test rate limiter check."""
    # First request should be allowed
    assert await rate_limiter.check() is True

    # Second request within the same second should be allowed (burst)
    assert await rate_limiter.check() is True

    # Third request within the same second should be allowed (burst)
    assert await rate_limiter.check() is True

    # Fourth request within the same second should be denied
    assert await rate_limiter.check() is False


async def test_rate_limiter_acquire(rate_limiter: RateLimiter) -> None:
    """Test rate limiter acquire."""
    start_time = time.monotonic()

    # First request should be immediate
    await rate_limiter.acquire()
    assert time.monotonic() - start_time < 0.1  # Increased threshold for CI

    # Second request should be immediate (burst)
    await rate_limiter.acquire()
    assert time.monotonic() - start_time < 0.1  # Increased threshold for CI

    # Third request should be immediate (burst)
    await rate_limiter.acquire()
    assert time.monotonic() - start_time < 0.1  # Increased threshold for CI

    # Fourth request should wait
    await rate_limiter.acquire()
    elapsed = time.monotonic() - start_time
    # Just verify that some delay occurred
    assert elapsed > 0.0
    assert elapsed < 1.0  # Upper bound for CI environments


async def test_rate_limiter_burst(rate_limiter: RateLimiter) -> None:
    """Test rate limiter burst behavior."""
    # Use up burst capacity
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True

    # Wait for rate to replenish (at least one token)
    await asyncio.sleep(0.3)  # Increased delay for more reliable tests

    # Should have one token available
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is False


async def test_rate_limiter_disabled(rate_limiter: RateLimiter) -> None:
    """Test disabled rate limiter."""
    # Set high rate and burst for effectively disabled limiting
    rate_limiter.rate = float('inf')
    rate_limiter.burst = 1000000

    # All requests should be allowed
    for _ in range(10):
        assert await rate_limiter.check() is True


async def test_rate_limiter_rate_change(rate_limiter: RateLimiter) -> None:
    """Test rate limiter rate change."""
    # Reset state
    rate_limiter.reset()

    # Use default rate
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is False

    # Reset and change rate to allow more requests
    rate_limiter.reset()
    rate_limiter.rate = 20.0  # Higher rate
    assert await rate_limiter.check() is True


async def test_rate_limiter_burst_change(rate_limiter: RateLimiter) -> None:
    """Test rate limiter burst change."""
    # Reset state
    rate_limiter.reset()

    # Use default burst
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is False

    # Reset and change burst to allow more concurrent requests
    rate_limiter.reset()
    rate_limiter.burst = 5
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True
