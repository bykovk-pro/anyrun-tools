"""Configuration for ANY.RUN API client."""

from typing import Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from .constants import (
    API_BASE_URL,
    DEFAULT_CACHE_PREFIX,
    DEFAULT_CACHE_TTL,
    DEFAULT_RATE_LIMIT,
    DEFAULT_RATE_LIMIT_WINDOW,
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    MAX_RETRY_DELAY,
    APIVersion,
)
from .types import CacheBackend, LogLevel, RateLimitBackend, RetryStrategy


class BaseConfig(BaseModel):
    """Base configuration model."""

    model_config = ConfigDict(
        validate_assignment=True, arbitrary_types_allowed=True, extra="allow"
    )

    api_key: str = Field(..., description="API key")
    base_url: HttpUrl = Field(default=HttpUrl(API_BASE_URL), description="Base URL")
    api_version: APIVersion = Field(default=APIVersion.V1, description="API version")
    timeout: float = Field(
        default=float(DEFAULT_TIMEOUT), description="Request timeout in seconds"
    )
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    proxies: Optional[Dict[str, str]] = Field(None, description="HTTP/HTTPS proxies")
    user_agent: Optional[str] = Field(None, description="User agent string")
    headers: Dict[str, str] = Field(
        default_factory=dict, description="Additional headers"
    )

    # Cache settings
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_backend: CacheBackend = Field(
        default=CacheBackend.MEMORY, description="Cache backend"
    )
    cache_ttl: int = Field(
        default=DEFAULT_CACHE_TTL, description="Cache TTL in seconds"
    )
    cache_prefix: str = Field(
        default=DEFAULT_CACHE_PREFIX, description="Cache key prefix"
    )

    # Rate limit settings
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_backend: RateLimitBackend = Field(
        default=RateLimitBackend.MEMORY, description="Rate limit backend"
    )
    rate_limit: int = Field(
        default=DEFAULT_RATE_LIMIT, description="Rate limit (requests per second)"
    )
    rate_limit_window: float = Field(
        default=DEFAULT_RATE_LIMIT_WINDOW, description="Rate limit window in seconds"
    )

    # Retry settings
    retry_enabled: bool = Field(default=True, description="Enable retries")
    retry_strategy: RetryStrategy = Field(
        default=RetryStrategy.EXPONENTIAL, description="Retry strategy"
    )
    retry_max_attempts: int = Field(
        default=DEFAULT_RETRY_COUNT, description="Maximum retry attempts"
    )
    retry_initial_delay: float = Field(
        default=DEFAULT_RETRY_DELAY, description="Initial retry delay in seconds"
    )
    retry_max_delay: float = Field(
        default=MAX_RETRY_DELAY, description="Maximum retry delay in seconds"
    )
    retry_backoff_factor: float = Field(default=2.0, description="Retry backoff factor")

    # Logging settings
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    log_format: str = Field(
        default="[{time}] {level} {message}",
        description="Log format string",
    )

    @field_validator("base_url", mode="before")
    @classmethod
    def validate_base_url(cls, v: Union[str, HttpUrl]) -> HttpUrl:
        """Validate and convert base_url to HttpUrl."""
        if isinstance(v, str):
            return HttpUrl(v)
        return v
