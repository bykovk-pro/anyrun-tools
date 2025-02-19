"""Tests for Sandbox API schemas."""

import pytest
from pydantic import ValidationError, HttpUrl

from anyrun.sandbox.schemas import (
    ObjectType,
    OSType,
    BitnessType,
    WindowsVersion,
    LinuxVersion,
    EnvType,
    Browser,
    PrivacyType,
    StartFolder,
    AnalysisRequest,
)


def test_object_type_enum():
    """Test ObjectType enum."""
    assert ObjectType.FILE == "file"
    assert ObjectType.URL == "url"
    assert ObjectType.DOWNLOAD == "download"
    assert ObjectType.RERUN == "rerun"
    assert len(ObjectType) == 4


def test_os_type_enum():
    """Test OSType enum."""
    assert OSType.WINDOWS == "windows"
    assert OSType.LINUX == "linux"
    assert len(OSType) == 2


def test_bitness_type_enum():
    """Test BitnessType enum."""
    assert BitnessType.X32 == "32"
    assert BitnessType.X64 == "64"
    assert len(BitnessType) == 2


def test_windows_version_enum():
    """Test WindowsVersion enum."""
    assert WindowsVersion.WIN7 == "7"
    assert WindowsVersion.WIN10 == "10"
    assert WindowsVersion.WIN11 == "11"
    assert len(WindowsVersion) == 3


def test_linux_version_enum():
    """Test LinuxVersion enum."""
    assert LinuxVersion.UBUNTU_22_04_2 == "22.04.2"
    assert len(LinuxVersion) == 1


def test_env_type_enum():
    """Test EnvType enum."""
    assert EnvType.CLEAN == "clean"
    assert EnvType.OFFICE == "office"
    assert EnvType.COMPLETE == "complete"
    assert len(EnvType) == 3


def test_browser_enum():
    """Test Browser enum."""
    assert Browser.CHROME == "Google Chrome"
    assert Browser.FIREFOX == "Mozilla Firefox"
    assert Browser.IE == "Internet Explorer"
    assert Browser.EDGE == "Microsoft Edge"
    assert len(Browser) == 4


def test_privacy_type_enum():
    """Test PrivacyType enum."""
    assert PrivacyType.PUBLIC == "public"
    assert PrivacyType.BYLINK == "bylink"
    assert PrivacyType.OWNER == "owner"
    assert PrivacyType.BYTEAM == "byteam"
    assert len(PrivacyType) == 4


def test_start_folder_enum():
    """Test StartFolder enum."""
    assert StartFolder.DESKTOP == "desktop"
    assert StartFolder.DOWNLOADS == "downloads"
    assert StartFolder.HOME == "home"
    assert StartFolder.TEMP == "temp"
    assert StartFolder.APPDATA == "appdata"
    assert StartFolder.ROOT == "root"
    assert StartFolder.WINDOWS == "windows"
    assert len(StartFolder) == 7


def test_analysis_request_file():
    """Test AnalysisRequest model with file object."""
    request = AnalysisRequest(
        obj_type=ObjectType.FILE,
        obj_content="base64_content",
        obj_filename="test.exe",
        env_os=OSType.WINDOWS,
        env_bitness=BitnessType.X64,
        env_version=WindowsVersion.WIN10,
        env_type=EnvType.CLEAN,
    )
    assert request.obj_type == ObjectType.FILE
    assert request.obj_content == "base64_content"
    assert request.obj_filename == "test.exe"
    assert request.env_os == OSType.WINDOWS
    assert request.env_bitness == BitnessType.X64
    assert request.env_version == WindowsVersion.WIN10
    assert request.env_type == EnvType.CLEAN


def test_analysis_request_url():
    """Test AnalysisRequest model with URL object."""
    request = AnalysisRequest(
        obj_type=ObjectType.URL,
        obj_url="https://example.com",
        env_os=OSType.WINDOWS,
        env_bitness=BitnessType.X64,
        env_version=WindowsVersion.WIN10,
        env_type=EnvType.CLEAN,
    )
    assert request.obj_type == ObjectType.URL
    assert isinstance(request.obj_url, HttpUrl)
    assert str(request.obj_url) == "https://example.com/"
    assert request.env_os == OSType.WINDOWS
    assert request.env_bitness == BitnessType.X64
    assert request.env_version == WindowsVersion.WIN10
    assert request.env_type == EnvType.CLEAN


def test_analysis_request_download():
    """Test AnalysisRequest model with download object."""
    request = AnalysisRequest(
        obj_type=ObjectType.DOWNLOAD,
        obj_url="https://example.com/file.exe",
        env_os=OSType.WINDOWS,
        env_bitness=BitnessType.X64,
        env_version=WindowsVersion.WIN10,
        env_type=EnvType.CLEAN,
    )
    assert request.obj_type == ObjectType.DOWNLOAD
    assert isinstance(request.obj_url, HttpUrl)
    assert str(request.obj_url) == "https://example.com/file.exe"
    assert request.env_os == OSType.WINDOWS
    assert request.env_bitness == BitnessType.X64
    assert request.env_version == WindowsVersion.WIN10
    assert request.env_type == EnvType.CLEAN


def test_analysis_request_rerun():
    """Test AnalysisRequest model with rerun object."""
    request = AnalysisRequest(
        obj_type=ObjectType.RERUN,
        obj_hash="hash123",
        env_os=OSType.WINDOWS,
        env_bitness=BitnessType.X64,
        env_version=WindowsVersion.WIN10,
        env_type=EnvType.CLEAN,
    )
    assert request.obj_type == ObjectType.RERUN
    assert request.obj_hash == "hash123"
    assert request.env_os == OSType.WINDOWS
    assert request.env_bitness == BitnessType.X64
    assert request.env_version == WindowsVersion.WIN10
    assert request.env_type == EnvType.CLEAN


def test_analysis_request_validation_file():
    """Test AnalysisRequest validation for file object."""
    with pytest.raises(ValidationError) as exc_info:
        AnalysisRequest(
            obj_type=ObjectType.FILE,
            env_os=OSType.WINDOWS,
            env_bitness=BitnessType.X64,
            env_version=WindowsVersion.WIN10,
            env_type=EnvType.CLEAN,
        )
    assert "Object content is required for file analysis" in str(exc_info.value)


def test_analysis_request_validation_url():
    """Test AnalysisRequest validation for URL object."""
    with pytest.raises(ValidationError) as exc_info:
        AnalysisRequest(
            obj_type=ObjectType.URL,
            env_os=OSType.WINDOWS,
            env_bitness=BitnessType.X64,
            env_version=WindowsVersion.WIN10,
            env_type=EnvType.CLEAN,
        )
    assert "Object URL is required for URL analysis" in str(exc_info.value)


def test_analysis_request_validation_download():
    """Test AnalysisRequest validation for download object."""
    with pytest.raises(ValidationError) as exc_info:
        AnalysisRequest(
            obj_type=ObjectType.DOWNLOAD,
            env_os=OSType.WINDOWS,
            env_bitness=BitnessType.X64,
            env_version=WindowsVersion.WIN10,
            env_type=EnvType.CLEAN,
        )
    assert "Object URL is required for download analysis" in str(exc_info.value)


def test_analysis_request_validation_rerun():
    """Test AnalysisRequest validation for rerun object."""
    with pytest.raises(ValidationError) as exc_info:
        AnalysisRequest(
            obj_type=ObjectType.RERUN,
            env_os=OSType.WINDOWS,
            env_bitness=BitnessType.X64,
            env_version=WindowsVersion.WIN10,
            env_type=EnvType.CLEAN,
        )
    assert "Object hash is required for rerun analysis" in str(exc_info.value)


def test_analysis_request_validation_windows11():
    """Test AnalysisRequest validation for Windows 11."""
    with pytest.raises(ValidationError) as exc_info:
        AnalysisRequest(
            obj_type=ObjectType.FILE,
            obj_content="base64_content",
            obj_filename="test.exe",
            env_os=OSType.WINDOWS,
            env_bitness=BitnessType.X32,
            env_version=WindowsVersion.WIN11,
            env_type=EnvType.CLEAN,
        )
    assert "Windows 11 supports only 64-bit" in str(exc_info.value)


def test_analysis_request_validation_linux():
    """Test AnalysisRequest validation for Linux."""
    with pytest.raises(ValidationError) as exc_info:
        AnalysisRequest(
            obj_type=ObjectType.FILE,
            obj_content="base64_content",
            obj_filename="test.exe",
            env_os=OSType.LINUX,
            env_bitness=BitnessType.X32,
            env_version=LinuxVersion.UBUNTU_22_04_2,
            env_type=EnvType.CLEAN,
        )
    assert "Linux supports only 64-bit" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        AnalysisRequest(
            obj_type=ObjectType.FILE,
            obj_content="base64_content",
            obj_filename="test.exe",
            env_os=OSType.LINUX,
            env_bitness=BitnessType.X64,
            env_version=LinuxVersion.UBUNTU_22_04_2,
            env_type=EnvType.CLEAN,
        )
    assert "Linux supports only office environment" in str(exc_info.value)


def test_analysis_request_validation_browser():
    """Test AnalysisRequest validation for browser."""
    # Windows browser validation
    with pytest.raises(ValidationError) as exc_info:
        AnalysisRequest(
            obj_type=ObjectType.FILE,
            obj_content="base64_content",
            obj_filename="test.exe",
            env_os=OSType.WINDOWS,
            env_bitness=BitnessType.X64,
            env_version=WindowsVersion.WIN10,
            env_type=EnvType.CLEAN,
            env_browser="Opera",
        )
    assert "Input should be 'Google Chrome', 'Mozilla Firefox', 'Internet Explorer' or 'Microsoft Edge'" in str(exc_info.value)

    # Linux browser validation
    with pytest.raises(ValidationError) as exc_info:
        AnalysisRequest(
            obj_type=ObjectType.FILE,
            obj_content="base64_content",
            obj_filename="test.exe",
            env_os=OSType.LINUX,
            env_bitness=BitnessType.X64,
            env_version=LinuxVersion.UBUNTU_22_04_2,
            env_type=EnvType.OFFICE,
            env_browser=Browser.IE,
            obj_ext_elevateprompt=False,  # Disable UAC options
            obj_force_elevation=False,
            auto_confirm_uac=False,
        )
    assert "Invalid browser for Linux. Supported: Google Chrome, Mozilla Firefox" in str(exc_info.value) 