"""Tests for caching utilities."""

import os
import asyncio
import pytest
from redis.asyncio import Redis
from redis.exceptions import ConnectionError
from typing import AsyncGenerator

from anyrun.utils.cache import Cache, MemoryCache, RedisCache


async def is_redis_available() -> bool:
    """Check if Redis is available.
    
    Returns:
        bool: True if Redis is available, False otherwise
    """
    try:
        redis = Redis(host="localhost", port=6379, db=0)
        await redis.ping()
        await redis.aclose()
        return True
    except (ConnectionError, OSError):
        return False


# Skip all Redis tests if Redis is not available
redis_not_available = asyncio.run(is_redis_available()) is False
skip_redis_message = "Redis server is not available"


@pytest.fixture
def memory_cache() -> Cache:
    """Get memory cache instance."""
    return Cache(backend=MemoryCache(prefix="anyrun:"), enabled=True)


@pytest.fixture
async def redis_client() -> AsyncGenerator[Redis, None]:
    """Get Redis client instance."""
    client = Redis(host="localhost", port=6379, db=0)
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.fixture
async def redis_cache(redis_client: Redis) -> Cache:
    """Get Redis cache instance."""
    return Cache(backend=RedisCache(redis_client, prefix="anyrun:"), enabled=True)


async def test_memory_cache_set_get(memory_cache: Cache) -> None:
    """Test memory cache set and get operations."""
    await memory_cache.set("test_key", "test_value")
    value = await memory_cache.get("test_key")
    assert value == "test_value"


async def test_memory_cache_delete(memory_cache: Cache) -> None:
    """Test memory cache delete operation."""
    await memory_cache.set("test_key", "test_value")
    await memory_cache.delete("test_key")
    value = await memory_cache.get("test_key")
    assert value is None


async def test_memory_cache_ttl(memory_cache: Cache) -> None:
    """Test memory cache TTL."""
    await memory_cache.set("test_key", "test_value", ttl=1)
    value = await memory_cache.get("test_key")
    assert value == "test_value"

    # Wait for TTL to expire
    await asyncio.sleep(2)
    value = await memory_cache.get("test_key")
    assert value is None


async def test_memory_cache_disabled(memory_cache: Cache) -> None:
    """Test disabled memory cache."""
    memory_cache.enabled = False
    await memory_cache.set("test_key", "test_value")
    value = await memory_cache.get("test_key")
    assert value is None


async def test_memory_cache_prefix(memory_cache: Cache) -> None:
    """Test memory cache key prefix."""
    memory_cache.prefix = "test:"
    memory_cache.backend.prefix = "test:"  # Update backend prefix too
    await memory_cache.set("key", "value")
    value = await memory_cache.get("key")
    assert value == "value"

    # Check that the key is stored with prefix
    raw_value = await memory_cache.backend.get("key")  # type: ignore
    assert raw_value == "value"


@pytest.mark.skipif(redis_not_available, reason=skip_redis_message)
async def test_redis_cache_set_get(redis_cache: Cache) -> None:
    """Test Redis cache set and get operations."""
    await redis_cache.set("test_key", "test_value")
    value = await redis_cache.get("test_key")
    assert value == "test_value"


@pytest.mark.skipif(redis_not_available, reason=skip_redis_message)
async def test_redis_cache_delete(redis_cache: Cache) -> None:
    """Test Redis cache delete operation."""
    await redis_cache.set("test_key", "test_value")
    await redis_cache.delete("test_key")
    value = await redis_cache.get("test_key")
    assert value is None


@pytest.mark.skipif(redis_not_available, reason=skip_redis_message)
async def test_redis_cache_ttl(redis_cache: Cache) -> None:
    """Test Redis cache TTL."""
    await redis_cache.set("test_key", "test_value", ttl=1)
    value = await redis_cache.get("test_key")
    assert value == "test_value"

    # Wait for TTL to expire
    await asyncio.sleep(2)
    value = await redis_cache.get("test_key")
    assert value is None


@pytest.mark.skipif(redis_not_available, reason=skip_redis_message)
async def test_redis_cache_disabled(redis_cache: Cache) -> None:
    """Test disabled Redis cache."""
    redis_cache.enabled = False
    await redis_cache.set("test_key", "test_value")
    value = await redis_cache.get("test_key")
    assert value is None


@pytest.mark.skipif(redis_not_available, reason=skip_redis_message)
async def test_redis_cache_prefix(redis_cache: Cache) -> None:
    """Test Redis cache key prefix."""
    # Clear Redis first
    await redis_cache.backend.client.flushdb()  # type: ignore

    # Test with default prefix
    await redis_cache.set("key", "value")
    value = await redis_cache.get("key")
    assert value == "value"

    # Check that the key is stored with default prefix
    raw_value = await redis_cache.backend.client.get("anyrun:key")  # type: ignore
    assert raw_value == b'"value"'  # Redis returns JSON-encoded bytes

    # Change prefix and test again
    redis_cache.prefix = "test:"
    await redis_cache.set("key", "new_value")
    value = await redis_cache.get("key")
    assert value == "new_value"

    # Check that the key is stored with new prefix
    raw_value = await redis_cache.backend.client.get("test:key")  # type: ignore
    assert raw_value == b'"new_value"'  # Redis returns JSON-encoded bytes

    # Also check that old key still exists (with old prefix)
    old_value = await redis_cache.backend.client.get("anyrun:key")  # type: ignore
    assert old_value == b'"value"'
