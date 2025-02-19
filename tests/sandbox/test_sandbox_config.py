"""Tests for Sandbox API configuration."""

import pytest
from pydantic import ValidationError

from anyrun.sandbox.config import SandboxConfig
from anyrun.constants import APIVersion


def test_sandbox_config_defaults():
    """Test SandboxConfig with default values."""
    config = SandboxConfig(
        api_key="test_key",
        base_url="https://api.any.run",
    )
    assert config.api_version == APIVersion.V1
    assert config.auto_download_files is True
    assert config.download_timeout == 300
    assert config.max_file_size == 100 * 1024 * 1024  # 100MB
    assert config.monitor_timeout == 1800  # 30 minutes
    assert config.monitor_interval == 1.0
    assert config.environment_cache_ttl == 3600  # 1 hour
    assert config.analysis_cache_ttl == 60  # 1 minute
    assert config.analyze_rate_limit == 0.2  # 10 per minute
    assert config.list_rate_limit == 1.0  # 60 per minute
    assert config.status_rate_limit == 2.0  # 120 per minute
    assert config.download_rate_limit == 0.5  # 30 per minute


def test_sandbox_config_custom():
    """Test SandboxConfig with custom values."""
    config = SandboxConfig(
        api_key="test_key",
        base_url="https://api.any.run",
        api_version=APIVersion.V1,
        auto_download_files=False,
        download_timeout=600,
        max_file_size=50 * 1024 * 1024,  # 50MB
        monitor_timeout=3600,
        monitor_interval=2.0,
        environment_cache_ttl=7200,
        analysis_cache_ttl=120,
        analyze_rate_limit=0.5,
        list_rate_limit=2.0,
        status_rate_limit=5.0,
        download_rate_limit=1.0,
    )
    assert config.api_version == APIVersion.V1
    assert config.auto_download_files is False
    assert config.download_timeout == 600
    assert config.max_file_size == 50 * 1024 * 1024
    assert config.monitor_timeout == 3600
    assert config.monitor_interval == 2.0
    assert config.environment_cache_ttl == 7200
    assert config.analysis_cache_ttl == 120
    assert config.analyze_rate_limit == 0.5
    assert config.list_rate_limit == 2.0
    assert config.status_rate_limit == 5.0
    assert config.download_rate_limit == 1.0


def test_sandbox_config_validation():
    """Test SandboxConfig validation."""
    # Test required fields
    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig()
    assert "Field required" in str(exc_info.value)
    assert "api_key" in str(exc_info.value)
    assert "base_url" in str(exc_info.value)

    # Test download_timeout validation
    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            download_timeout=0,
        )
    assert "greater than or equal to 1" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            download_timeout=3601,
        )
    assert "less than or equal to 3600" in str(exc_info.value)

    # Test max_file_size validation
    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            max_file_size=0,
        )
    assert "greater than or equal to 1" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            max_file_size=501 * 1024 * 1024,  # 501MB
        )
    assert "less than or equal to" in str(exc_info.value)

    # Test monitor_timeout validation
    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            monitor_timeout=0,
        )
    assert "greater than or equal to 1" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            monitor_timeout=7201,  # 2 hours + 1 second
        )
    assert "less than or equal to 7200" in str(exc_info.value)

    # Test monitor_interval validation
    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            monitor_interval=0.05,
        )
    assert "greater than or equal to 0.1" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            monitor_interval=60.1,
        )
    assert "Input should be less than or equal to 60" in str(exc_info.value)

    # Test cache TTL validation
    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            environment_cache_ttl=0,
        )
    assert "greater than or equal to 1" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            analysis_cache_ttl=0,
        )
    assert "greater than or equal to 1" in str(exc_info.value)

    # Test rate limits validation
    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            analyze_rate_limit=-0.1,
        )
    assert "Input should be greater than or equal to 0" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            analyze_rate_limit=10.1,
        )
    assert "Input should be less than or equal to 10" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            list_rate_limit=10.1,
        )
    assert "Input should be less than or equal to 10" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            status_rate_limit=10.1,
        )
    assert "Input should be less than or equal to 10" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            download_rate_limit=10.1,
        )
    assert "Input should be less than or equal to 10" in str(exc_info.value)


def test_sandbox_config_extra_fields():
    """Test SandboxConfig extra fields validation."""
    with pytest.raises(ValidationError) as exc_info:
        SandboxConfig(
            api_key="test_key",
            base_url="https://api.any.run",
            unknown_field="value",
        )
    assert "Extra inputs are not permitted" in str(exc_info.value) 