"""Tests for caching utilities."""

import pytest
from redis.asyncio import Redis

from anyrun.utils.cache import Cache, MemoryCache


@pytest.fixture
def memory_cache() -> Cache:
    """Get memory cache instance."""
    return Cache(backend=MemoryCache(prefix="anyrun:"), enabled=True)


@pytest.fixture
async def redis_cache() -> Cache:
    """Get Redis cache instance."""
    redis = Redis(host="localhost", port=6379, db=0)
    cache = Cache(backend=redis, enabled=True)
    yield cache
    await redis.close()


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
    import asyncio
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


@pytest.mark.skip("Requires Redis server")
async def test_redis_cache_set_get(redis_cache: Cache) -> None:
    """Test Redis cache set and get operations."""
    await redis_cache.set("test_key", "test_value")
    value = await redis_cache.get("test_key")
    assert value == "test_value"


@pytest.mark.skip("Requires Redis server")
async def test_redis_cache_delete(redis_cache: Cache) -> None:
    """Test Redis cache delete operation."""
    await redis_cache.set("test_key", "test_value")
    await redis_cache.delete("test_key")
    value = await redis_cache.get("test_key")
    assert value is None


@pytest.mark.skip("Requires Redis server")
async def test_redis_cache_ttl(redis_cache: Cache) -> None:
    """Test Redis cache TTL."""
    await redis_cache.set("test_key", "test_value", ttl=1)
    value = await redis_cache.get("test_key")
    assert value == "test_value"

    # Wait for TTL to expire
    import asyncio
    await asyncio.sleep(2)
    value = await redis_cache.get("test_key")
    assert value is None


@pytest.mark.skip("Requires Redis server")
async def test_redis_cache_disabled(redis_cache: Cache) -> None:
    """Test disabled Redis cache."""
    redis_cache.enabled = False
    await redis_cache.set("test_key", "test_value")
    value = await redis_cache.get("test_key")
    assert value is None


@pytest.mark.skip("Requires Redis server")
async def test_redis_cache_prefix(redis_cache: Cache) -> None:
    """Test Redis cache key prefix."""
    redis_cache.prefix = "test:"
    await redis_cache.set("key", "value")
    value = await redis_cache.get("key")
    assert value == "value"

    # Check that the key is stored with prefix
    raw_value = await redis_cache.backend.get("test:key")  # type: ignore
    assert raw_value == b"value"  # Redis returns bytes
