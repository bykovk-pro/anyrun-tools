"""Common types for ANY.RUN Tools."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class APIVersion(str, Enum):
    """API version."""

    V1 = "v1"
    V2 = "v2"


class APIResponse(BaseModel):
    """Base API response model."""

    error: bool = Field(description="Error flag")
    data: dict[str, Any] = Field(description="Response data")
    message: str | None = Field(None, description="Optional message")


class FileUpload(BaseModel):
    """File upload model."""

    content: str | bytes = Field(description="File content or path")
    filename: str = Field(description="File name")
    content_type: str | None = Field(None, description="Content type")


class APIKey(BaseModel):
    """API key model."""

    key: str = Field(description="API key value")
    name: str | None = Field(None, description="Key name")
    created_at: datetime = Field(description="Creation timestamp")
    expires_at: datetime | None = Field(None, description="Expiration timestamp")
    is_active: bool = Field(default=True, description="Key status")
    permissions: dict[str, bool] = Field(default_factory=dict, description="Key permissions")


class Pagination(BaseModel):
    """Pagination parameters."""

    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=25, ge=1, le=100, description="Number of items per page")
    total: int | None = Field(None, description="Total number of items")


class WebhookConfig(BaseModel):
    """Webhook configuration."""

    url: HttpUrl = Field(description="Webhook URL")
    secret: str | None = Field(None, description="Webhook secret")
    events: list[str] = Field(description="Event types to subscribe to")
    is_active: bool = Field(default=True, description="Webhook status")
    retry_count: int = Field(default=3, ge=0, le=10, description="Number of retry attempts")
    timeout: int = Field(default=30, ge=1, le=60, description="Request timeout in seconds")


class CacheBackend(str, Enum):
    """Cache backend type."""

    MEMORY = "memory"
    REDIS = "redis"
    NONE = "none"


class RateLimitBackend(str, Enum):
    """Rate limit backend type."""

    MEMORY = "memory"
    REDIS = "redis"
    NONE = "none"


class RetryStrategy(str, Enum):
    """Retry strategy type."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    NONE = "none"


class LogLevel(str, Enum):
    """Log level type."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BaseConfig(BaseModel):
    """Base configuration model."""

    api_key: str = Field(..., description="API key")
    base_url: HttpUrl = Field(..., description="Base URL")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    proxies: dict[str, str] | None = Field(None, description="HTTP/HTTPS proxies")
    user_agent: str | None = Field(None, description="User agent string")
    headers: dict[str, str] = Field(default_factory=dict, description="Additional headers")

    # Cache settings
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_backend: CacheBackend = Field(default=CacheBackend.MEMORY, description="Cache backend")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    cache_prefix: str = Field(default="anyrun:", description="Cache key prefix")

    # Rate limit settings
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_backend: RateLimitBackend = Field(
        default=RateLimitBackend.MEMORY, description="Rate limit backend"
    )
    rate_limit: int = Field(default=10, description="Rate limit (requests per second)")
    rate_limit_window: float = Field(default=1.0, description="Rate limit window in seconds")

    # Retry settings
    retry_enabled: bool = Field(default=True, description="Enable retries")
    retry_strategy: RetryStrategy = Field(
        default=RetryStrategy.EXPONENTIAL, description="Retry strategy"
    )
    retry_max_attempts: int = Field(default=3, description="Maximum retry attempts")
    retry_initial_delay: float = Field(default=1.0, description="Initial retry delay in seconds")
    retry_max_delay: float = Field(default=60.0, description="Maximum retry delay in seconds")
    retry_backoff_factor: float = Field(default=2.0, description="Retry backoff factor")

    # Logging settings
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    log_format: str = Field(
        default="[{time}] {level} {message}",
        description="Log format string",
    )
