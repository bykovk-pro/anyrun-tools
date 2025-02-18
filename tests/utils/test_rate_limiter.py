"""Tests for rate limiter utilities."""

import asyncio
import time

import pytest

from anyrun.utils import RateLimiter


@pytest.fixture
def rate_limiter() -> RateLimiter:
    """Get rate limiter instance."""
    return RateLimiter(rate=2.0, burst=3, key="test")


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
    start_time = time.time()

    # First request should be immediate
    await rate_limiter.acquire()
    assert time.time() - start_time < 0.1

    # Second request should be immediate (burst)
    await rate_limiter.acquire()
    assert time.time() - start_time < 0.1

    # Third request should be immediate (burst)
    await rate_limiter.acquire()
    assert time.time() - start_time < 0.1

    # Fourth request should wait
    await rate_limiter.acquire()
    assert time.time() - start_time >= 0.5  # At least 0.5s delay


async def test_rate_limiter_burst(rate_limiter: RateLimiter) -> None:
    """Test rate limiter burst behavior."""
    # Use up burst capacity
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True

    # Wait for rate to replenish
    await asyncio.sleep(1.0)

    # Should have one token available
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is False


async def test_rate_limiter_disabled(rate_limiter: RateLimiter) -> None:
    """Test disabled rate limiter."""
    rate_limiter.enabled = False

    # All requests should be allowed
    for _ in range(10):
        assert await rate_limiter.check() is True
        await rate_limiter.acquire()  # Should not wait


async def test_rate_limiter_rate_change(rate_limiter: RateLimiter) -> None:
    """Test rate limiter rate change."""
    # Use default rate
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is False

    # Change rate to allow more requests
    rate_limiter.rate = 10.0
    assert await rate_limiter.check() is True


async def test_rate_limiter_burst_change(rate_limiter: RateLimiter) -> None:
    """Test rate limiter burst change."""
    # Use default burst
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is False

    # Change burst to allow more concurrent requests
    rate_limiter.burst = 5
    assert await rate_limiter.check() is True
    assert await rate_limiter.check() is True 