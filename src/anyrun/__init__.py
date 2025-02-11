"""ANY.RUN Tools - Python SDK for ANY.RUN APIs."""

from importlib import metadata

from .client import AnyRunClient
from .config import BaseConfig
from .exceptions import (
    AnyRunError,
    APIError,
    AuthenticationError,
    ConfigurationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)

try:
    __version__ = metadata.version("anyrun-tools")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.1.0"

__all__ = [
    "__version__",
    "AnyRunClient",
    "BaseConfig",
    # Exceptions
    "AnyRunError",
    "APIError",
    "AuthenticationError",
    "ConfigurationError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
]
