"""Tests for rate limiter utilities."""

import asyncio
import time

import pytest

from anyrun.utils import RateLimiter


@pytest.fixture
def rate_limiter() -> RateLimiter:
    """Get rate limiter instance."""
    return RateLimiter(rate=10.0, burst=3, key="test")  # Higher rate for faster tests


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
    assert time.monotonic() - start_time < 0.01

    # Second request should be immediate (burst)
    await rate_limiter.acquire()
    assert time.monotonic() - start_time < 0.01

    # Third request should be immediate (burst)
    await rate_limiter.acquire()
    assert time.monotonic() - start_time < 0.01

    # Fourth request should wait
    await rate_limiter.acquire()
    assert 0.1 <= time.monotonic() - start_time <= 0.2  # Shorter delay


async def test_rate_limiter_burst(rate_limiter: RateLimiter) -> None:
    """Test rate limiter burst behavior."""
    # Use up burst capacity
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True

    # Wait for rate to replenish
    await asyncio.sleep(0.1)  # Shorter delay

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
