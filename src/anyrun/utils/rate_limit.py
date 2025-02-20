"""Rate limiting implementation for ANY.RUN Tools."""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional


class RateLimitError(Exception):
    """Error raised when rate limit is exceeded."""

    def __init__(
        self, message: str = "Rate limit exceeded", retry_after: Optional[float] = None
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Number of seconds to wait before retrying
        """
        if retry_after is not None:
            message = f"{message}. Please wait {retry_after:.1f} seconds."
        super().__init__(message)
        self.retry_after = retry_after


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
        else:
            # Reset state for testing
            self._state[self.key]["tokens"] = float(self.burst)
            self._state[self.key]["last_update"] = time.monotonic()

    async def _ensure_lock(self) -> asyncio.Lock:
        """Ensure lock exists and return it.

        Returns:
            asyncio.Lock: The lock instance
        """
        state = self._state[self.key]
        if state["lock"] is None:
            state["lock"] = asyncio.Lock()
        lock = state["lock"]
        assert isinstance(lock, asyncio.Lock)  # for mypy
        return lock

    async def acquire(self) -> None:
        """Acquire token from rate limiter.

        Raises:
            RateLimitError: If no tokens available
        """
        if not await self.check():
            needed = 1.0
            retry_after = needed / self.rate if self.rate > 0 else float("inf")
            raise RateLimitError(retry_after=retry_after)

    async def check(self) -> bool:
        """Check if token is available.

        Returns:
            bool: True if token is available
        """
        if self.rate <= 0:
            return True

        lock = await self._ensure_lock()
        async with lock:
            state = self._state[self.key]
            now = time.monotonic()
            time_passed = now - state["last_update"]
            new_tokens = time_passed * self.rate
            state["tokens"] = min(float(self.burst), state["tokens"] + new_tokens)
            state["last_update"] = now

            if state["tokens"] >= 1.0:
                state["tokens"] -= 1.0
                return True
            return False

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
            new_tokens = float(time_passed * self.rate)
            tokens = float(state["tokens"])
            return min(float(self.burst), tokens + new_tokens)
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
