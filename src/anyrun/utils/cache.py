"""Cache implementation for ANY.RUN Tools."""

import json
import time
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional, Protocol, Tuple, TypeVar, Union

from loguru import logger
from redis.asyncio import Redis

if TYPE_CHECKING:
    from redis.asyncio import Redis

T = TypeVar("T")


class CacheBackend(Protocol):
    """Abstract base class for cache backends."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Any: Cached value or None if not found
        """

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key
        """

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key exists, False otherwise
        """


class Cache:
    """Cache wrapper with backend selection."""

    def __init__(
        self,
        backend: Optional[Union[CacheBackend, Redis]] = None,
        enabled: bool = True,
        prefix: str = "anyrun:",
        default_ttl: int = 300,
    ) -> None:
        """Initialize cache.

        Args:
            backend: Cache backend instance
            enabled: Whether cache is enabled
            prefix: Key prefix
            default_ttl: Default TTL in seconds
        """
        self.enabled = enabled
        self.prefix = prefix
        self.default_ttl = default_ttl

        if not enabled:
            self.backend: CacheBackend = NoCache()
        elif backend is None:
            self.backend = MemoryCache()
        elif isinstance(backend, (RedisCache, MemoryCache, NoCache)):
            self.backend = backend
        elif isinstance(backend, Redis):
            self.backend = RedisCache(backend, prefix, default_ttl)
        else:
            raise ValueError("Invalid cache backend")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Any: Cached value or None if not found
        """
        if not self.enabled:
            return None
        return await self.backend.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        if not self.enabled:
            return
        await self.backend.set(key, value, ttl or self.default_ttl)

    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key
        """
        if not self.enabled:
            return
        await self.backend.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key exists, False otherwise
        """
        if not self.enabled:
            return False
        return await self.backend.exists(key)


class RedisCache(CacheBackend):
    """Redis cache backend implementation."""

    def __init__(
        self,
        client: Redis,
        prefix: str = "anyrun:",
        default_ttl: int = 300,
    ) -> None:
        """Initialize Redis cache.

        Args:
            client: Redis client instance
            prefix: Key prefix
            default_ttl: Default TTL in seconds
        """
        self.client = client
        self.prefix = prefix
        self.default_ttl = default_ttl

    def _get_key(self, key: str) -> str:
        """Get prefixed key.

        Args:
            key: Cache key

        Returns:
            str: Prefixed key
        """
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache.

        Args:
            key: Cache key

        Returns:
            Any: Cached value or None if not found
        """
        try:
            value = await self.client.get(self._get_key(key))
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.warning(f"Failed to get value from Redis cache: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in Redis cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        try:
            await self.client.set(
                self._get_key(key),
                json.dumps(value),
                ex=ttl or self.default_ttl,
            )
        except Exception as e:
            logger.warning(f"Failed to set value in Redis cache: {e}")

    async def delete(self, key: str) -> None:
        """Delete value from Redis cache.

        Args:
            key: Cache key
        """
        try:
            await self.client.delete(self._get_key(key))
        except Exception as e:
            logger.warning(f"Failed to delete value from Redis cache: {e}")

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key exists, False otherwise
        """
        try:
            return bool(await self.client.exists(self._get_key(key)))
        except Exception as e:
            logger.warning(f"Failed to check key existence in Redis cache: {e}")
            return False


class NoCache(CacheBackend):
    """No-op cache backend implementation."""

    async def get(self, key: str) -> None:
        """Always return None.

        Args:
            key: Cache key

        Returns:
            None: Always returns None
        """
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Do nothing.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """

    async def delete(self, key: str) -> None:
        """Do nothing.

        Args:
            key: Cache key
        """

    async def exists(self, key: str) -> bool:
        """Always return False.

        Args:
            key: Cache key

        Returns:
            bool: Always returns False
        """
        return False


class MemoryCache(CacheBackend):
    """In-memory cache backend implementation."""

    def __init__(self, prefix: str = "anyrun:", default_ttl: int = 300) -> None:
        """Initialize in-memory cache.

        Args:
            prefix: Key prefix
            default_ttl: Default TTL in seconds
        """
        self._cache: Dict[str, Tuple[Any, Optional[float]]] = {}
        self.prefix = prefix
        self.default_ttl = default_ttl

    def _get_key(self, key: str) -> str:
        """Get prefixed key.

        Args:
            key: Cache key

        Returns:
            str: Prefixed key
        """
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache.

        Args:
            key: Cache key

        Returns:
            Any: Cached value or None if not found
        """
        key = self._get_key(key)
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]
        if expiry is not None and time.time() > expiry:
            del self._cache[key]
            return None

        return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in memory cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        key = self._get_key(key)
        expiry = time.time() + (ttl or self.default_ttl) if ttl is not None else None
        self._cache[key] = (value, expiry)

    async def delete(self, key: str) -> None:
        """Delete value from memory cache.

        Args:
            key: Cache key
        """
        key = self._get_key(key)
        self._cache.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key exists and not expired, False otherwise
        """
        key = self._get_key(key)
        if key not in self._cache:
            return False

        _, expiry = self._cache[key]
        if expiry is not None and time.time() > expiry:
            del self._cache[key]
            return False

        return True


def get_cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    """Generate a cache key from prefix and arguments.

    Args:
        prefix: Cache key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Generated cache key
    """
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)


def get_ttl(key: str, default: Optional[int] = None) -> Optional[int]:
    """Get TTL for cache key.

    Args:
        key: Cache key
        default: Default TTL value

    Returns:
        TTL value in seconds or None if not set
    """
