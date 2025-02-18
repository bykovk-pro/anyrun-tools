"""Configuration for ANY.RUN API client."""

from typing import Dict, TypeVar

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, ValidationInfo, field_validator

from .constants import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT
from .types import CacheBackend, LogLevel, RetryStrategy

T = TypeVar("T", bound="BaseConfig")


class BaseConfig(BaseModel):
    """Base configuration for ANY.RUN client."""

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=False,
        extra="ignore",
    )

    # API configuration
    api_key: str = Field(min_length=1, description="ANY.RUN API key")
    base_url: HttpUrl = Field(description="Base URL for API requests")
    api_version: str = Field(default="v1", description="API version")

    # HTTP client configuration
    timeout: float = Field(default=DEFAULT_TIMEOUT, ge=0, description="Request timeout in seconds")
    user_agent: str = Field(default=DEFAULT_USER_AGENT, description="User agent string")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    headers: Dict[str, str] = Field(
        default_factory=lambda: {"User-Agent": DEFAULT_USER_AGENT},
        description="Additional HTTP headers",
    )

    @field_validator("headers")  # type: ignore[misc]
    @classmethod
    def merge_headers(cls, v: Dict[str, str], values: ValidationInfo) -> Dict[str, str]:
        """Merge custom headers with default headers.

        Args:
            v: Custom headers
            values: Values being validated

        Returns:
            Dict[str, str]: Merged headers
        """
        result = {"User-Agent": values.data.get("user_agent", DEFAULT_USER_AGENT)}
        result.update(v)
        return result

    # Cache configuration
    cache_enabled: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=300, ge=0, description="Cache TTL in seconds")
    cache_backend: CacheBackend = Field(
        default=CacheBackend.MEMORY,
        description="Cache backend type",
    )

    # Rate limiting configuration
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")

    # Retry configuration
    retry_strategy: RetryStrategy = Field(
        default=RetryStrategy.EXPONENTIAL,
        description="Retry strategy",
    )
    retry_max_attempts: int = Field(default=3, ge=1, description="Maximum retry attempts")
    retry_initial_delay: float = Field(
        default=1.0, ge=0, description="Initial retry delay in seconds"
    )
    retry_max_delay: float = Field(default=60.0, ge=0, description="Maximum retry delay in seconds")

    # Logging settings
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    log_format: str = Field(
        default="[{time}] {level} {message}",
        description="Log format string",
    )
