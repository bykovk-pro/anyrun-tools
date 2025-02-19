"""Tests for Sandbox API constants."""

from anyrun.sandbox.constants import (
    SUPPORTED_OS_TYPES,
    SUPPORTED_WINDOWS_VERSIONS,
    SUPPORTED_LINUX_VERSIONS,
    SUPPORTED_BITNESS,
    SUPPORTED_ENV_TYPES,
    SUPPORTED_BROWSERS,
    DEFAULT_BROWSERS,
    SUPPORTED_START_FOLDERS,
    PRIVACY_TYPES,
    MAX_FILE_SIZE,
    MAX_MEMORY_SIZE,
    DEFAULT_MONITOR_TIMEOUT,
    DEFAULT_MONITOR_INTERVAL,
    DEFAULT_DOWNLOAD_TIMEOUT,
)


def test_supported_os_types():
    """Test supported OS types."""
    assert isinstance(SUPPORTED_OS_TYPES, set)
    assert "windows" in SUPPORTED_OS_TYPES
    assert "linux" in SUPPORTED_OS_TYPES
    assert len(SUPPORTED_OS_TYPES) == 2


def test_supported_windows_versions():
    """Test supported Windows versions."""
    assert isinstance(SUPPORTED_WINDOWS_VERSIONS, set)
    assert "7" in SUPPORTED_WINDOWS_VERSIONS
    assert "10" in SUPPORTED_WINDOWS_VERSIONS
    assert "11" in SUPPORTED_WINDOWS_VERSIONS
    assert len(SUPPORTED_WINDOWS_VERSIONS) == 3


def test_supported_linux_versions():
    """Test supported Linux versions."""
    assert isinstance(SUPPORTED_LINUX_VERSIONS, set)
    assert "22.04.2" in SUPPORTED_LINUX_VERSIONS
    assert len(SUPPORTED_LINUX_VERSIONS) == 1


def test_supported_bitness():
    """Test supported bitness."""
    assert isinstance(SUPPORTED_BITNESS, dict)
    assert "windows" in SUPPORTED_BITNESS
    assert "linux" in SUPPORTED_BITNESS
    assert isinstance(SUPPORTED_BITNESS["windows"], set)
    assert isinstance(SUPPORTED_BITNESS["linux"], set)
    assert "32" in SUPPORTED_BITNESS["windows"]
    assert "64" in SUPPORTED_BITNESS["windows"]
    assert "64" in SUPPORTED_BITNESS["linux"]
    assert len(SUPPORTED_BITNESS["windows"]) == 2
    assert len(SUPPORTED_BITNESS["linux"]) == 1


def test_supported_env_types():
    """Test supported environment types."""
    assert isinstance(SUPPORTED_ENV_TYPES, dict)
    assert "windows" in SUPPORTED_ENV_TYPES
    assert "linux" in SUPPORTED_ENV_TYPES
    assert isinstance(SUPPORTED_ENV_TYPES["windows"], set)
    assert isinstance(SUPPORTED_ENV_TYPES["linux"], set)
    assert "clean" in SUPPORTED_ENV_TYPES["windows"]
    assert "office" in SUPPORTED_ENV_TYPES["windows"]
    assert "complete" in SUPPORTED_ENV_TYPES["windows"]
    assert "office" in SUPPORTED_ENV_TYPES["linux"]
    assert len(SUPPORTED_ENV_TYPES["windows"]) == 3
    assert len(SUPPORTED_ENV_TYPES["linux"]) == 1


def test_supported_browsers():
    """Test supported browsers."""
    assert isinstance(SUPPORTED_BROWSERS, dict)
    assert "windows" in SUPPORTED_BROWSERS
    assert "linux" in SUPPORTED_BROWSERS
    assert isinstance(SUPPORTED_BROWSERS["windows"], set)
    assert isinstance(SUPPORTED_BROWSERS["linux"], set)
    assert "Google Chrome" in SUPPORTED_BROWSERS["windows"]
    assert "Mozilla Firefox" in SUPPORTED_BROWSERS["windows"]
    assert "Internet Explorer" in SUPPORTED_BROWSERS["windows"]
    assert "Microsoft Edge" in SUPPORTED_BROWSERS["windows"]
    assert "Google Chrome" in SUPPORTED_BROWSERS["linux"]
    assert "Mozilla Firefox" in SUPPORTED_BROWSERS["linux"]
    assert len(SUPPORTED_BROWSERS["windows"]) == 4
    assert len(SUPPORTED_BROWSERS["linux"]) == 2


def test_default_browsers():
    """Test default browsers."""
    assert isinstance(DEFAULT_BROWSERS, dict)
    assert "windows" in DEFAULT_BROWSERS
    assert "linux" in DEFAULT_BROWSERS
    assert DEFAULT_BROWSERS["windows"] == "Microsoft Edge"
    assert DEFAULT_BROWSERS["linux"] == "Google Chrome"
    assert len(DEFAULT_BROWSERS) == 2


def test_supported_start_folders():
    """Test supported start folders."""
    assert isinstance(SUPPORTED_START_FOLDERS, dict)
    assert "windows" in SUPPORTED_START_FOLDERS
    assert "linux" in SUPPORTED_START_FOLDERS
    assert isinstance(SUPPORTED_START_FOLDERS["windows"], set)
    assert isinstance(SUPPORTED_START_FOLDERS["linux"], set)
    # Windows folders
    assert "appdata" in SUPPORTED_START_FOLDERS["windows"]
    assert "desktop" in SUPPORTED_START_FOLDERS["windows"]
    assert "downloads" in SUPPORTED_START_FOLDERS["windows"]
    assert "home" in SUPPORTED_START_FOLDERS["windows"]
    assert "root" in SUPPORTED_START_FOLDERS["windows"]
    assert "temp" in SUPPORTED_START_FOLDERS["windows"]
    assert "windows" in SUPPORTED_START_FOLDERS["windows"]
    assert len(SUPPORTED_START_FOLDERS["windows"]) == 7
    # Linux folders
    assert "desktop" in SUPPORTED_START_FOLDERS["linux"]
    assert "downloads" in SUPPORTED_START_FOLDERS["linux"]
    assert "home" in SUPPORTED_START_FOLDERS["linux"]
    assert "temp" in SUPPORTED_START_FOLDERS["linux"]
    assert len(SUPPORTED_START_FOLDERS["linux"]) == 4


def test_privacy_types():
    """Test privacy types."""
    assert isinstance(PRIVACY_TYPES, set)
    assert "public" in PRIVACY_TYPES
    assert "bylink" in PRIVACY_TYPES
    assert "owner" in PRIVACY_TYPES
    assert "byteam" in PRIVACY_TYPES
    assert len(PRIVACY_TYPES) == 4


def test_size_limits():
    """Test size limits."""
    assert isinstance(MAX_FILE_SIZE, int)
    assert isinstance(MAX_MEMORY_SIZE, int)
    assert MAX_FILE_SIZE == 100 * 1024 * 1024  # 100MB
    assert MAX_MEMORY_SIZE == 500 * 1024 * 1024  # 500MB


def test_timeouts():
    """Test timeout values."""
    assert isinstance(DEFAULT_MONITOR_TIMEOUT, int)
    assert isinstance(DEFAULT_MONITOR_INTERVAL, float)
    assert isinstance(DEFAULT_DOWNLOAD_TIMEOUT, int)
    assert DEFAULT_MONITOR_TIMEOUT == 1800  # 30 minutes
    assert DEFAULT_MONITOR_INTERVAL == 1.0  # 1 second
    assert DEFAULT_DOWNLOAD_TIMEOUT == 300  # 5 minutes 