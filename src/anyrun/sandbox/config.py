"""Configuration for Sandbox API."""

from pydantic import ConfigDict, Field

from ..config import BaseConfig
from ..constants import APIVersion
from .constants import (
    SUPPORTED_BROWSERS,
    SUPPORTED_ENV_TYPES,
    SUPPORTED_LINUX_VERSIONS,
    SUPPORTED_OS_TYPES,
    SUPPORTED_START_FOLDERS,
    SUPPORTED_WINDOWS_VERSIONS,
)
from .schemas import OSType


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

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=True,
        extra="forbid",
    )

    def validate_env_version(self) -> None:
        """Validate environment version."""
        if self.os_type == OSType.WINDOWS:
            if self.env_version not in SUPPORTED_WINDOWS_VERSIONS:
                raise ValueError(
                    f"Unsupported Windows version: {self.env_version}. "
                    f"Supported versions: {SUPPORTED_WINDOWS_VERSIONS}"
                )
        elif self.os_type == OSType.LINUX:
            if self.env_version not in SUPPORTED_LINUX_VERSIONS:
                raise ValueError(
                    f"Unsupported Linux version: {self.env_version}. "
                    f"Supported versions: {SUPPORTED_LINUX_VERSIONS}"
                )

    def validate_os_type(self) -> None:
        """Validate operating system type."""
        if self.os_type not in SUPPORTED_OS_TYPES:
            raise ValueError(
                f"Unsupported operating system type: {self.os_type}. "
                f"Supported types: {SUPPORTED_OS_TYPES}"
            )

    def validate_start_folder(self) -> None:
        """Validate start folder."""
        if self.start_folder not in SUPPORTED_START_FOLDERS:
            raise ValueError(
                f"Unsupported start folder: {self.start_folder}. "
                f"Supported folders: {SUPPORTED_START_FOLDERS}"
            )

    def validate_env_type(self) -> None:
        """Validate environment type."""
        if self.env_type not in SUPPORTED_ENV_TYPES:
            raise ValueError(
                f"Unsupported environment type: {self.env_type}. "
                f"Supported types: {SUPPORTED_ENV_TYPES}"
            )

    def validate_browser(self) -> None:
        """Validate browser."""
        if self.browser is not None and self.browser not in SUPPORTED_BROWSERS:
            raise ValueError(
                f"Unsupported browser: {self.browser}. " f"Supported browsers: {SUPPORTED_BROWSERS}"
            )

    def validate_timeout(self) -> None:
        """Validate timeout."""
        if self.timeout < 0:
            raise ValueError("Timeout must be non-negative")

    def validate(self) -> None:
        """Validate configuration."""
        self.validate_env_version()
        self.validate_os_type()
        self.validate_start_folder()
        self.validate_env_type()
        self.validate_browser()
        self.validate_timeout()
