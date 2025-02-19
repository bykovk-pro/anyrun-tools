"""Constants for Sandbox API."""

from typing import Dict, Final, Set

# API endpoints
ENDPOINT_ANALYSIS: Final[str] = "/analysis"
ENDPOINT_ANALYSIS_STATUS: Final[str] = "/analysis/status/{task_id}"
ENDPOINT_ANALYSIS_MONITOR: Final[str] = "/analysis/monitor/{task_id}"
ENDPOINT_ANALYSIS_ADD_TIME: Final[str] = "/analysis/addtime/{task_id}"
ENDPOINT_ANALYSIS_STOP: Final[str] = "/analysis/stop/{task_id}"
ENDPOINT_ANALYSIS_DELETE: Final[str] = "/analysis/delete/{task_id}"
ENDPOINT_ENVIRONMENT: Final[str] = "/environment"
ENDPOINT_USER: Final[str] = "/user"
ENDPOINT_USER_PRESETS: Final[str] = "/user/presets"

# Cache keys
CACHE_KEY_ENVIRONMENT: Final[str] = "sandbox:environment"
CACHE_KEY_USER_INFO: Final[str] = "sandbox:user_info"
CACHE_KEY_USER_PRESETS: Final[str] = "sandbox:user_presets"
CACHE_KEY_ANALYSIS: Final[str] = "sandbox:analysis:{task_id}"

# Default values
DEFAULT_TIMEOUT: Final[int] = 30
DEFAULT_CACHE_TTL: Final[int] = 300
DEFAULT_RATE_LIMIT: Final[float] = 1.0
DEFAULT_USER_AGENT: Final[str] = "anyrun-tools/sandbox"

# File size limits
MAX_FILE_SIZE: Final[int] = 100 * 1024 * 1024  # 100MB
MAX_MEMORY_SIZE: Final[int] = 500 * 1024 * 1024  # 500MB

# Analysis settings
DEFAULT_MONITOR_TIMEOUT: Final[int] = 1800  # 30 minutes
DEFAULT_MONITOR_INTERVAL: Final[float] = 1.0  # 1 second
DEFAULT_DOWNLOAD_TIMEOUT: Final[int] = 300  # 5 minutes

# Environment settings
SUPPORTED_OS_TYPES: Final[Set[str]] = {"windows", "linux"}

SUPPORTED_WINDOWS_VERSIONS: Final[Set[str]] = {"7", "10", "11"}

SUPPORTED_LINUX_VERSIONS: Final[Set[str]] = {"22.04.2"}  # Ubuntu

SUPPORTED_BITNESS: Final[Dict[str, Set[str]]] = {
    "windows": {"32", "64"},
    "linux": {"64"},
}

SUPPORTED_ENV_TYPES: Final[Dict[str, Set[str]]] = {
    "windows": {"clean", "office", "complete"},
    "linux": {"office"},
}

SUPPORTED_BROWSERS: Final[Dict[str, Set[str]]] = {
    "windows": {
        "Google Chrome",
        "Mozilla Firefox",
        "Internet Explorer",
        "Microsoft Edge",
    },
    "linux": {"Google Chrome", "Mozilla Firefox"},
}

DEFAULT_BROWSERS: Final[Dict[str, str]] = {
    "windows": "Microsoft Edge",
    "linux": "Google Chrome",
}

# Start folders
SUPPORTED_START_FOLDERS: Final[Dict[str, Set[str]]] = {
    "windows": {"appdata", "desktop", "downloads", "home", "root", "temp", "windows"},
    "linux": {"desktop", "downloads", "home", "temp"},
}

# Privacy types
PRIVACY_TYPES: Final[Set[str]] = {"public", "bylink", "owner", "byteam"}

# Analysis status codes
STATUS_QUEUED: Final[str] = "queued"
STATUS_RUNNING: Final[str] = "running"
STATUS_COMPLETED: Final[str] = "completed"
STATUS_FAILED: Final[str] = "failed"
STATUS_STOPPED: Final[str] = "stopped"
STATUS_DELETED: Final[str] = "deleted"

# Analysis events
EVENT_STARTED: Final[str] = "analysis.started"
EVENT_FINISHED: Final[str] = "analysis.finished"
EVENT_FAILED: Final[str] = "analysis.failed"
EVENT_STOPPED: Final[str] = "analysis.stopped"
EVENT_DELETED: Final[str] = "analysis.deleted"

# File extensions
SUPPORTED_EXTENSIONS: Final[Dict[str, Set[str]]] = {
    "executables": {".exe", ".dll", ".sys", ".scr", ".com"},
    "scripts": {".ps1", ".vbs", ".js", ".jse", ".hta"},
    "documents": {".doc", ".docx", ".xls", ".xlsx", ".pdf"},
    "archives": {".zip", ".7z", ".rar", ".tar", ".gz"},
}

# Error messages
ERROR_INVALID_OS: Final[str] = "Invalid operating system. Supported: {}"
ERROR_INVALID_VERSION: Final[str] = "Invalid {} version. Supported: {}"
ERROR_INVALID_BITNESS: Final[str] = "Invalid bitness for {}. Supported: {}"
ERROR_INVALID_ENV_TYPE: Final[str] = "Invalid environment type for {}. Supported: {}"
ERROR_INVALID_BROWSER: Final[str] = "Invalid browser for {}. Supported: {}"
ERROR_INVALID_START_FOLDER: Final[str] = "Invalid start folder for {}. Supported: {}"
ERROR_INVALID_PRIVACY: Final[str] = "Invalid privacy type. Supported: {}"
ERROR_INVALID_FILE_EXT: Final[str] = "Invalid file extension. Supported: {}"
ERROR_FILE_TOO_LARGE: Final[str] = "File size exceeds limit of {} bytes"
ERROR_TASK_NOT_FOUND: Final[str] = "Analysis task not found: {}"
ERROR_TASK_COMPLETED: Final[str] = "Analysis task already completed: {}"
ERROR_TASK_FAILED: Final[str] = "Analysis task failed: {}"
