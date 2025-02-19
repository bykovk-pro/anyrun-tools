"""Tests for rate limiter utilities."""

import asyncio
import time

import pytest
from pytest import mark

from anyrun.utils.rate_limit import RateLimiter, RateLimitError


@pytest.fixture
def rate_limiter() -> RateLimiter:
    """Get rate limiter instance."""
    return RateLimiter(rate=5.0, burst=3, key="test")  # Lower rate for more predictable tests


@mark.asyncio
async def test_rate_limiter_check(rate_limiter: RateLimiter) -> None:
    """Test rate limiter check method."""
    assert await rate_limiter.check()  # First request should pass
    assert await rate_limiter.check()  # Second request should pass
    assert await rate_limiter.check()  # Third request should pass
    assert not await rate_limiter.check()  # Fourth request should fail


@mark.asyncio
async def test_rate_limiter_acquire(rate_limiter: RateLimiter) -> None:
    """Test rate limiter acquire method."""
    await rate_limiter.acquire()  # First request should pass
    await rate_limiter.acquire()  # Second request should pass
    await rate_limiter.acquire()  # Third request should pass
    with pytest.raises(RateLimitError):
        await rate_limiter.acquire()  # Fourth request should fail


@mark.asyncio
async def test_rate_limiter_burst(rate_limiter: RateLimiter) -> None:
    """Test rate limiter burst behavior."""
    # Should allow burst requests
    assert await rate_limiter.check()
    assert await rate_limiter.check()
    assert await rate_limiter.check()
    assert not await rate_limiter.check()

    # Wait for tokens to refill
    await asyncio.sleep(1.0)
    assert await rate_limiter.check()  # Should have ~5 new tokens


@mark.asyncio
async def test_rate_limiter_disabled(rate_limiter: RateLimiter) -> None:
    """Test disabled rate limiter."""
    rate_limiter.rate = 0
    assert await rate_limiter.check()
    assert await rate_limiter.check()
    assert await rate_limiter.check()
    assert await rate_limiter.check()


@mark.asyncio
async def test_rate_limiter_rate_change(rate_limiter: RateLimiter) -> None:
    """Test rate limiter with rate change."""
    assert await rate_limiter.check()
    assert await rate_limiter.check()
    assert await rate_limiter.check()
    assert not await rate_limiter.check()

    # Change rate and wait
    rate_limiter.rate = 10.0
    await asyncio.sleep(0.5)
    assert await rate_limiter.check()  # Should have ~5 new tokens


@mark.asyncio
async def test_rate_limiter_burst_change(rate_limiter: RateLimiter) -> None:
    """Test rate limiter with burst change."""
    assert await rate_limiter.check()
    assert await rate_limiter.check()
    assert await rate_limiter.check()
    assert not await rate_limiter.check()

    # Change burst and reset
    rate_limiter.burst = 5
    rate_limiter.reset()
    assert await rate_limiter.check()
    assert await rate_limiter.check()
    assert await rate_limiter.check()
    assert await rate_limiter.check()
    assert await rate_limiter.check()
    assert not await rate_limiter.check()
