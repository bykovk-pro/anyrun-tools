"""Rate limiting implementation for ANY.RUN Tools."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, TypedDict, ClassVar, Any

from loguru import logger


class RateLimitError(Exception):
    """Error raised when rate limit is exceeded."""

    def __init__(self, retry_after: float) -> None:
        """Initialize rate limit error.

        Args:
            retry_after: Number of seconds to wait before retrying
        """
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Please wait {retry_after:.1f} seconds.")


class RateLimiterState(TypedDict):
    """Rate limiter state type."""

    tokens: float
    last_update: float
    lock: Optional[asyncio.Lock]


@dataclass
class RateLimiter:
    """Rate limiter implementation."""

    rate: float
    burst: float
    key: str = "default"

    _state: ClassVar[Dict[str, Dict[str, Any]]] = {}

    def __post_init__(self) -> None:
        """Initialize rate limiter state."""
        if self.key not in self._state:
            self._state[self.key] = {
                "tokens": float(self.burst),
                "last_update": time.monotonic(),
                "lock": None,
            }

    async def _ensure_lock(self) -> asyncio.Lock:
        """Ensure lock exists and return it.

        Returns:
            asyncio.Lock: The lock instance
        """
        state = self._state[self.key]
        if state["lock"] is None:
            state["lock"] = asyncio.Lock()
        assert state["lock"] is not None  # for mypy
        return state["lock"]

    async def acquire(self) -> None:
        """Acquire token from rate limiter.

        Raises:
            RateLimitError: If no tokens available
        """
        if not await self.check():
            raise RateLimitError("Rate limit exceeded")

    async def check(self) -> bool:
        """Check if token is available.

        Returns:
            bool: True if token is available
        """
        if self.rate <= 0 or self.burst <= 0:
            return True

        lock = await self._ensure_lock()
        async with lock:
            return await self._get_available_tokens() > 0

    async def _get_available_tokens(self) -> float:
        """Get available tokens.

        Returns:
            float: Number of available tokens
        """
        state = self._state[self.key]
        now = time.monotonic()
        time_passed = now - state["last_update"]
        state["tokens"] = min(
            self.burst,
            state["tokens"] + time_passed * self.rate,
        )
        state["last_update"] = now

        if state["tokens"] < 1:
            return 0

        state["tokens"] -= 1
        return state["tokens"]

    def reset(self) -> None:
        """Reset rate limiter state."""
        if self.key in self._state:
            self._state[self.key]["tokens"] = float(self.burst)
            self._state[self.key]["last_update"] = time.monotonic()

    def get_available_tokens(self) -> float:
        """Get number of available tokens.

        Returns:
            float: Number of available tokens
        """
        try:
            state = self._state[self.key]
            now = time.monotonic()
            time_passed = now - state["last_update"]
            return min(state["tokens"] + time_passed * self.rate, float(self.burst))
        except Exception:
            return 0.0

    def get_state(self) -> dict:
        """Get the current state of the rate limiter.

        Returns:
            dict: The current state of the rate limiter
        """
        return {
            "limit": self.burst,
            "remaining": self.get_available_tokens(),
            "reset": self.reset,
        }
