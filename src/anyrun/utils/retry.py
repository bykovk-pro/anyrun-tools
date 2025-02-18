"""Retry mechanism for ANY.RUN Tools."""

from __future__ import annotations

import asyncio
import functools
import random
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional, TypeVar, Union

from loguru import logger
from typing_extensions import ParamSpec

from anyrun.exceptions import APIError, RateLimitError, RetryError, ServerError

T = TypeVar("T")
P = ParamSpec("P")


@dataclass
class RetryConfig:
    """Configuration for retry mechanism."""

    max_attempts: int = 3
    """Maximum number of retry attempts."""

    delay: float = 1.0
    """Base delay between attempts in seconds."""

    max_delay: float = 60.0
    """Maximum delay between attempts in seconds."""

    exponential: bool = True
    """Whether to use exponential backoff."""

    jitter: bool = True
    """Whether to add random jitter to delay."""

    exceptions: Union[type[Exception], list[type[Exception]], None] = None
    """Exception types to retry on. If None, retry on all exceptions."""


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    max_delay: float = 60.0,
    exponential: bool = True,
    jitter: bool = True,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Retry decorator for async functions.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts in seconds
        max_delay: Maximum delay between attempts in seconds
        exponential: Whether to use exponential backoff
        jitter: Whether to add jitter to delay

    Returns:
        Callable: Decorated function
    """

    def decorator(
        func: Callable[P, Awaitable[T]],
    ) -> Callable[P, Awaitable[T]]:
        """Decorator function.

        Args:
            func: Function to decorate

        Returns:
            Callable: Decorated function
        """

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Wrapper function.

            Args:
                *args: Positional arguments
                **kwargs: Keyword arguments

            Returns:
                Any: Function result

            Raises:
                RetryError: If all attempts fail
            """
            # Check if the first argument is a class instance with config attribute
            if args and hasattr(args[0], "config") and hasattr(args[0].config, "retry_enabled"):
                if not args[0].config.retry_enabled:
                    return await func(*args, **kwargs)

            attempt = 1
            current_delay = delay
            last_error: Optional[Union[RateLimitError, APIError]] = None

            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except RateLimitError as exc:
                    last_error = exc
                    if attempt >= max_attempts:
                        break

                    # Use retry_after from RateLimitError
                    current_delay = float(exc.retry_after if exc.retry_after is not None else delay)
                    logger.debug(
                        f"Attempt {attempt} failed with RateLimitError. "
                        f"Retrying in {current_delay:.2f} seconds..."
                    )

                    await asyncio.sleep(current_delay)
                    attempt += 1
                except (ServerError, APIError) as exc:
                    last_error = exc
                    if attempt >= max_attempts:
                        break

                    current_delay = min(
                        current_delay * 2 if exponential else current_delay,
                        max_delay,
                    )

                    if jitter:
                        current_delay *= random.uniform(0.5, 1.5)  # nosec B311

                    logger.debug(
                        f"Attempt {attempt} failed with {type(exc).__name__}. "
                        f"Retrying in {current_delay:.2f} seconds..."
                    )

                    await asyncio.sleep(current_delay)
                    attempt += 1

            if last_error:
                raise last_error
            raise RetryError(attempt, Exception("Unknown error"))

        return wrapper

    return decorator
