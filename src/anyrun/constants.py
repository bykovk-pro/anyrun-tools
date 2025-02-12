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
    "ti_lookup": {"hash": 60, "url": 60, "ip": 60, "domain": 60},
    "ti_yara": {"match": 30, "list": 60},
}

# Cache TTLs (seconds)
CACHE_TTLS: Final[Dict[str, int]] = {
    "environment": 3600,  # 1 hour
    "user_info": 300,  # 5 minutes
    "analysis": 60,  # 1 minute
    "ti_lookup": 1800,  # 30 minutes
    "ti_yara": 1800,  # 30 minutes
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
    "ti_lookup.matched",
    "ti_yara.matched",
)

# File extensions
SUPPORTED_EXTENSIONS: Final[Tuple[str, ...]] = (
    # Executables
    ".exe",
    ".dll",
    ".sys",
    ".scr",
    ".com",
    # Scripts
    ".ps1",
    ".vbs",
    ".js",
    ".jse",
    ".hta",
    # Documents
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".pdf",
    # Archives
    ".zip",
    ".7z",
    ".rar",
    ".tar",
    ".gz",
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

# File extensions
FILE_EXTENSIONS: Final[Tuple[str, ...]] = (
    ".exe",
    ".dll",
    ".sys",
    ".scr",
    ".cpl",
    ".ocx",
    ".ax",
    ".bin",
    ".cmd",
    ".bat",
    ".com",
    ".js",
    ".jse",
    ".vbs",
    ".vbe",
    ".wsf",
    ".wsh",
    ".ps1",
    ".msi",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".pdf",
    ".rtf",
    ".html",
    ".htm",
    ".hta",
    ".swf",
    ".jar",
    ".class",
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
    ".bz2",
    ".iso",
    ".img",
    ".vhd",
    ".vmdk",
    ".eml",
    ".msg",
    ".url",
    ".lnk",
    ".reg",
    ".inf",
    ".scf",
    ".job",
    ".tmp",
    ".dat",
    ".log",
    ".txt",
    ".cfg",
    ".ini",
    ".db",
    ".sqlite",
    ".mdb",
    ".accdb",
    ".pst",
    ".ost",
    ".bak",
    ".old",
    ".new",
)
