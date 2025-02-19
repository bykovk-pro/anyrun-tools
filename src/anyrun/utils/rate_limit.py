"""Rate limiting implementation for ANY.RUN Tools."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, TypedDict

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
    lock: asyncio.Lock


@dataclass
class RateLimiter:
    """Token bucket rate limiter implementation."""

    rate: float
    """Number of tokens per second."""

    burst: int
    """Maximum number of tokens that can be accumulated."""

    key: str = "default"
    """Rate limiter key for multiple limiters."""

    _state: Dict[str, RateLimiterState] = field(default_factory=dict)
    """Internal state for multiple rate limiters."""

    def __post_init__(self) -> None:
        """Initialize rate limiter state."""
        if self.key not in self._state:
            self._state[self.key] = {
                "tokens": float(self.burst),
                "last_update": time.monotonic(),
                "lock": asyncio.Lock(),
            }

    async def acquire(self, tokens: int = 1, wait: bool = True) -> None:
        """Acquire tokens from the bucket.

        Args:
            tokens: Number of tokens to acquire
            wait: Whether to wait for tokens to become available

        Raises:
            RateLimitError: If tokens are not available and wait is False
            ValueError: If requested tokens exceeds burst size
        """
        if tokens > self.burst:
            raise ValueError(f"Requested tokens ({tokens}) exceeds burst size ({self.burst})")

        state = self._state[self.key]
        async with state["lock"]:
            now = time.monotonic()
            time_passed = now - state["last_update"]

            # Add new tokens based on time passed
            new_tokens = time_passed * self.rate
            state["tokens"] = min(state["tokens"] + new_tokens, float(self.burst))
            state["last_update"] = now

            if state["tokens"] < tokens:
                if not wait:
                    # Calculate time needed for tokens to become available
                    needed = tokens - state["tokens"]
                    retry_after = needed / self.rate
                    raise RateLimitError(retry_after)

                # Wait for tokens to become available
                needed = tokens - state["tokens"]
                wait_time = needed / self.rate
                logger.debug(
                    f"Rate limit reached. Waiting {wait_time:.1f} seconds "
                    f"for {needed:.1f} tokens..."
                )
                await asyncio.sleep(wait_time)

                # Update state after waiting
                state["tokens"] = float(self.burst)
                state["last_update"] = time.monotonic()

            # Consume tokens
            state["tokens"] -= float(tokens)

    async def check(self, tokens: int = 1) -> bool:
        """Check if tokens are available and consume them if available.

        Args:
            tokens: Number of tokens to check

        Returns:
            bool: True if tokens are available and consumed, False otherwise
        """
        try:
            state = self._state[self.key]
            async with state["lock"]:
                now = time.monotonic()
                time_passed = now - state["last_update"]

                # Add new tokens based on time passed
                new_tokens = time_passed * self.rate
                state["tokens"] = min(state["tokens"] + new_tokens, float(self.burst))
                state["last_update"] = now

                # Check if we have enough tokens
                if state["tokens"] < tokens:
                    return False

                # Consume tokens
                state["tokens"] -= float(tokens)
                return True
        except Exception:
            return False

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

    def reset(self) -> None:
        """Reset rate limiter state."""
        state = self._state[self.key]
        state["tokens"] = float(self.burst)
        state["last_update"] = time.monotonic()

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
