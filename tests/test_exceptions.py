"""Tests for exceptions."""

import pytest

from anyrun.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


def test_api_error() -> None:
    """Test APIError."""
    error = APIError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_authentication_error() -> None:
    """Test AuthenticationError."""
    error = AuthenticationError("Invalid API key")
    assert str(error) == "Invalid API key"
    assert isinstance(error, APIError)


def test_not_found_error() -> None:
    """Test NotFoundError."""
    error = NotFoundError("Resource not found")
    assert str(error) == "Resource not found"
    assert isinstance(error, APIError)


def test_rate_limit_error() -> None:
    """Test RateLimitError."""
    error = RateLimitError("Rate limit exceeded", retry_after=60)
    assert str(error) == "Rate limit exceeded"
    assert error.retry_after == 60
    assert isinstance(error, APIError)


def test_server_error() -> None:
    """Test ServerError."""
    error = ServerError("Internal server error")
    assert str(error) == "Internal server error"
    assert isinstance(error, APIError)


def test_validation_error() -> None:
    """Test ValidationError."""
    error = ValidationError("Invalid data")
    assert str(error) == "Invalid data"
    assert isinstance(error, APIError)


def test_error_inheritance() -> None:
    """Test error inheritance."""
    errors = [
        AuthenticationError("Auth error"),
        NotFoundError("Not found"),
        RateLimitError("Rate limit", retry_after=60),
        ServerError("Server error"),
        ValidationError("Validation error"),
    ]

    for error in errors:
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)


def test_error_with_details() -> None:
    """Test error with additional details."""
    details = {"code": 404, "message": "Not found"}
    error = NotFoundError("Resource not found", details=details)
    assert str(error) == "Resource not found"
    assert error.details == details


def test_rate_limit_error_without_retry_after() -> None:
    """Test RateLimitError without retry_after."""
    error = RateLimitError("Rate limit exceeded")
    assert str(error) == "Rate limit exceeded"
    assert error.retry_after == 60  # Default value


def test_error_with_cause() -> None:
    """Test error with cause."""
    cause = ValueError("Original error")
    error = APIError("API error", cause=cause)
    assert str(error) == "API error"
    assert error.__cause__ == cause
