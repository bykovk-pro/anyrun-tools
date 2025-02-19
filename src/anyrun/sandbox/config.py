"""Configuration for Sandbox API."""

from pydantic import Field

from ..config import BaseConfig
from ..constants import APIVersion


class SandboxConfig(BaseConfig):
    """Configuration for Sandbox API."""

    # API settings
    api_version: APIVersion = Field(default=APIVersion.V1, description="Sandbox API version")

    # Analysis settings
    auto_download_files: bool = Field(
        default=True, description="Automatically download analysis files"
    )
    download_timeout: int = Field(
        default=300, ge=1, le=3600, description="Download timeout in seconds"
    )
    max_file_size: int = Field(
        default=100 * 1024 * 1024,  # 100MB
        ge=1,
        le=500 * 1024 * 1024,  # 500MB
        description="Maximum file size in bytes",
    )

    # Monitoring settings
    monitor_timeout: int = Field(
        default=1800,  # 30 minutes
        ge=1,
        le=7200,  # 2 hours
        description="Analysis monitoring timeout in seconds",
    )
    monitor_interval: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Analysis monitoring interval in seconds",
    )

    # Cache settings
    environment_cache_ttl: int = Field(
        default=3600,  # 1 hour
        ge=1,
        description="Environment info cache TTL in seconds",
    )
    analysis_cache_ttl: int = Field(
        default=60, ge=1, description="Analysis info cache TTL in seconds"  # 1 minute
    )

    # Rate limits (requests per second)
    analyze_rate_limit: float = Field(
        default=0.2,  # 10 per minute
        ge=0.0,
        le=10.0,
        description="Analysis creation rate limit",
    )
    list_rate_limit: float = Field(
        default=1.0,  # 60 per minute
        ge=0.0,
        le=10.0,
        description="Analysis list rate limit",
    )
    status_rate_limit: float = Field(
        default=2.0,  # 120 per minute
        ge=0.0,
        le=10.0,
        description="Analysis status rate limit",
    )
    download_rate_limit: float = Field(
        default=0.5,  # 30 per minute
        ge=0.0,
        le=10.0,
        description="File download rate limit",
    )

    class Config:
        """Pydantic model configuration."""

        validate_assignment = True
        extra = "forbid"
