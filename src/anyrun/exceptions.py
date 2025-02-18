"""Exceptions for ANY.RUN API client."""

from typing import Optional


class AnyRunError(Exception):
    """Base exception for ANY.RUN errors."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize exception.

        Args:
            message: Error message
            status_code: Optional HTTP status code
        """
        super().__init__(message)
        self.status_code = status_code


class APIError(AnyRunError):
    """Base exception for ANY.RUN API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize exception.

        Args:
            message: Error message
            status_code: Optional HTTP status code
        """
        super().__init__(message, status_code)


class RetryError(APIError):
    """Error raised when all retry attempts fail."""

    def __init__(self, attempts: int, last_error: Exception) -> None:
        """Initialize retry error.

        Args:
            attempts: Number of attempts made
            last_error: Last error encountered
        """
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"Failed after {attempts} attempts. Last error: {str(last_error)}")


class AuthenticationError(APIError):
    """Authentication error."""


class ConfigurationError(APIError):
    """Configuration error."""


class NotFoundError(APIError):
    """Resource not found error."""


class RateLimitError(APIError):
    """Rate limit exceeded error."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        """Initialize exception.

        Args:
            message: Error message
            status_code: Optional HTTP status code
            retry_after: Optional number of seconds to wait before retrying
        """
        super().__init__(message, status_code)
        self.retry_after = retry_after


class ServerError(APIError):
    """Server error."""


class ValidationError(APIError):
    """Validation error."""
