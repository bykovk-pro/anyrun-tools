"""Tests for configuration."""

from typing import Dict

import pytest
from pydantic import HttpUrl, ValidationError

from anyrun.config import BaseConfig
from anyrun.constants import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT
from anyrun.types import CacheBackend, RetryStrategy


def test_base_config_defaults() -> None:
    """Test base configuration defaults."""
    config = BaseConfig(
        api_key="test_key",
        base_url=HttpUrl("https://api.any.run"),
    )

    assert config.api_key == "test_key"
    assert str(config.base_url) == "https://api.any.run"
    assert config.api_version == "v1"
    assert config.timeout == DEFAULT_TIMEOUT
    assert config.user_agent == DEFAULT_USER_AGENT
    assert config.verify_ssl is True
    assert config.headers == {}
    assert config.proxies == {}
    assert config.cache_enabled is True
    assert config.cache_ttl == 300
    assert config.cache_backend == CacheBackend.MEMORY
    assert config.rate_limit_enabled is True
    assert config.retry_strategy == RetryStrategy.EXPONENTIAL
    assert config.retry_max_attempts == 3
    assert config.retry_initial_delay == 1.0
    assert config.retry_max_delay == 60.0


def test_base_config_custom_values() -> None:
    """Test base configuration with custom values."""
    config = BaseConfig(
        api_key="test_key",
        base_url=HttpUrl("https://api.any.run"),
        api_version="v2",
        timeout=30.0,
        user_agent="CustomAgent/1.0",
        verify_ssl=False,
        headers={"X-Custom": "value"},
        proxies={"http": "http://proxy:8080"},
        cache_enabled=False,
        cache_ttl=600,
        cache_backend=CacheBackend.REDIS,
        rate_limit_enabled=False,
        retry_strategy=RetryStrategy.LINEAR,
        retry_max_attempts=5,
        retry_initial_delay=2.0,
        retry_max_delay=120.0,
    )

    assert config.api_version == "v2"
    assert config.timeout == 30.0
    assert config.user_agent == "CustomAgent/1.0"
    assert config.verify_ssl is False
    assert config.headers == {"X-Custom": "value"}
    assert config.proxies == {"http": "http://proxy:8080"}
    assert config.cache_enabled is False
    assert config.cache_ttl == 600
    assert config.cache_backend == CacheBackend.REDIS
    assert config.rate_limit_enabled is False
    assert config.retry_strategy == RetryStrategy.LINEAR
    assert config.retry_max_attempts == 5
    assert config.retry_initial_delay == 2.0
    assert config.retry_max_delay == 120.0


def test_base_config_validation() -> None:
    """Test base configuration validation."""
    # Test invalid API key
    with pytest.raises(ValidationError):
        BaseConfig(
            api_key="",  # Empty API key
            base_url=HttpUrl("https://api.any.run"),
        )

    # Test invalid URL
    with pytest.raises(ValidationError):
        BaseConfig(
            api_key="test_key",
            base_url="invalid-url",  # type: ignore
        )

    # Test invalid timeout
    with pytest.raises(ValidationError):
        BaseConfig(
            api_key="test_key",
            base_url=HttpUrl("https://api.any.run"),
            timeout=-1,  # Negative timeout
        )

    # Test invalid cache TTL
    with pytest.raises(ValidationError):
        BaseConfig(
            api_key="test_key",
            base_url=HttpUrl("https://api.any.run"),
            cache_ttl=-1,  # Negative TTL
        )

    # Test invalid retry attempts
    with pytest.raises(ValidationError):
        BaseConfig(
            api_key="test_key",
            base_url=HttpUrl("https://api.any.run"),
            retry_max_attempts=0,  # Zero attempts
        )


def test_base_config_immutable_fields() -> None:
    """Test base configuration field immutability."""
    config = BaseConfig(
        api_key="test_key",
        base_url=HttpUrl("https://api.any.run"),
    )

    # Test that fields can be modified (not frozen)
    config.timeout = 30.0
    assert config.timeout == 30.0

    config.headers["X-Custom"] = "value"
    assert config.headers["X-Custom"] == "value"


def test_base_config_extra_fields() -> None:
    """Test base configuration extra fields handling."""
    config = BaseConfig(
        api_key="test_key",
        base_url=HttpUrl("https://api.any.run"),
        extra_field="ignored",  # Should be ignored
    )

    assert not hasattr(config, "extra_field")


def test_base_config_headers_merge() -> None:
    """Test base configuration headers merging."""
    default_headers = {"User-Agent": DEFAULT_USER_AGENT}
    custom_headers = {"X-Custom": "value"}

    config = BaseConfig(
        api_key="test_key",
        base_url=HttpUrl("https://api.any.run"),
        headers=custom_headers,
    )

    # Custom headers should not override default headers
    assert "User-Agent" in config.headers
    assert config.headers["X-Custom"] == "value"


def test_base_config_proxies_validation() -> None:
    """Test base configuration proxies validation."""
    valid_proxies: Dict[str, str] = {
        "http": "http://proxy:8080",
        "https": "https://proxy:8443",
    }
    invalid_proxies = {
        "http": "invalid-url",
        "https": "invalid-url",
    }

    # Test valid proxies
    config = BaseConfig(
        api_key="test_key",
        base_url=HttpUrl("https://api.any.run"),
        proxies=valid_proxies,
    )
    assert config.proxies == valid_proxies

    # Test invalid proxies
    with pytest.raises(ValidationError):
        BaseConfig(
            api_key="test_key",
            base_url=HttpUrl("https://api.any.run"),
            proxies=invalid_proxies,  # type: ignore
        )


def test_base_config_cache_backend_validation() -> None:
    """Test base configuration cache backend validation."""
    # Test valid cache backends
    for backend in CacheBackend:
        config = BaseConfig(
            api_key="test_key",
            base_url=HttpUrl("https://api.any.run"),
            cache_backend=backend,
        )
        assert config.cache_backend == backend

    # Test invalid cache backend
    with pytest.raises(ValidationError):
        BaseConfig(
            api_key="test_key",
            base_url=HttpUrl("https://api.any.run"),
            cache_backend="invalid",  # type: ignore
        )


def test_base_config_retry_strategy_validation() -> None:
    """Test base configuration retry strategy validation."""
    # Test valid retry strategies
    for strategy in RetryStrategy:
        config = BaseConfig(
            api_key="test_key",
            base_url=HttpUrl("https://api.any.run"),
            retry_strategy=strategy,
        )
        assert config.retry_strategy == strategy

    # Test invalid retry strategy
    with pytest.raises(ValidationError):
        BaseConfig(
            api_key="test_key",
            base_url=HttpUrl("https://api.any.run"),
            retry_strategy="invalid",  # type: ignore
        ) 