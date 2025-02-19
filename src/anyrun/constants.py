"""Common constants for ANY.RUN Tools."""

from enum import Enum
from typing import Dict, Final, Tuple

from ._version import __version__

# API URLs
API_BASE_URL: Final[str] = "https://api.any.run"
API_DOCS_URL: Final[str] = "https://api.any.run/docs"


# API versions
class APIVersion(str, Enum):
    """API version."""

    V1 = "v1"
    V2 = "v2"
    LATEST = V1


# HTTP headers
HEADER_API_KEY: Final[str] = "Authorization"
HEADER_USER_AGENT: Final[str] = "User-Agent"
DEFAULT_USER_AGENT: Final[str] = f"anyrun-tools/{__version__}"

# Request limits
MAX_FILE_SIZE: Final[int] = 100 * 1024 * 1024  # 100MB
MAX_URL_LENGTH: Final[int] = 2048
MAX_BATCH_SIZE: Final[int] = 100

# Rate limits (requests per minute)
RATE_LIMITS: Final[Dict[str, Dict[str, int]]] = {
    "sandbox": {"analyze": 10, "list": 60, "status": 120, "download": 30},
}

# Cache TTLs (seconds)
CACHE_TTLS: Final[Dict[str, int]] = {
    "environment": 3600,  # 1 hour
    "user_info": 300,  # 5 minutes
    "analysis": 60,  # 1 minute
}

# Retry configuration
DEFAULT_RETRY_COUNT: Final[int] = 3
DEFAULT_RETRY_DELAY: Final[float] = 1.0
MAX_RETRY_DELAY: Final[float] = 10.0

# Webhook events
WEBHOOK_EVENTS: Final[Tuple[str, ...]] = (
    "analysis.started",
    "analysis.finished",
    "analysis.failed",
)

# Environment defaults
DEFAULT_TIMEOUT: Final[float] = 30.0  # seconds
DEFAULT_CACHE_TTL: Final[int] = 300  # seconds
DEFAULT_CACHE_PREFIX: Final[str] = "anyrun:"

# Rate limit settings
DEFAULT_RATE_LIMIT: Final[int] = 10  # requests per second
DEFAULT_RATE_LIMIT_WINDOW: Final[float] = 1.0  # seconds

# HTTP status codes
HTTP_STATUS_CODES: Final[Dict[str, int]] = {
    "OK": 200,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "NOT_FOUND": 404,
    "TOO_MANY_REQUESTS": 429,
    "INTERNAL_SERVER_ERROR": 500,
}

# HTTP methods
HTTP_METHODS: Final[Tuple[str, ...]] = (
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "HEAD",
    "OPTIONS",
)
