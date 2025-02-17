"""Tests for Sandbox API models."""

from typing import Any, Dict, Optional, cast

import pytest
from pydantic import HttpUrl

from anyrun.sandbox.v1.models.analysis import (
    FileAnalysisRequest,
    URLAnalysisRequest,
    RerunAnalysisRequest,
    BitnessType,
    Browser,
    EnvType,
    LinuxVersion,
    ObjectType,
    OSType,
    PrivacyType,
    StartFolder,
    WindowsVersion,
)


def test_file_analysis_request() -> None:
    """Test file analysis request."""
    request = FileAnalysisRequest(
        file=b"test content",
        obj_url=None,
        task_rerun_uuid=None,
        env_os=OSType.WINDOWS,
        env_version=WindowsVersion.WIN10,
        env_bitness=BitnessType.X64,
        env_type=EnvType.CLEAN,
        obj_ext_browser=Browser.CHROME,
        obj_ext_startfolder=StartFolder.TEMP,
        opt_privacy_type=PrivacyType.BYLINK,
        env_locale=None,
        obj_ext_cmd=None,
        obj_ext_useragent=None,
        obj_ext_elevateprompt=None,
        obj_force_elevation=None,
        user_tags=None,
    )

    assert request.obj_type == ObjectType.FILE
    assert request.file == b"test content"
    assert request.env_os == OSType.WINDOWS
    assert request.env_version == WindowsVersion.WIN10
    assert request.env_bitness == BitnessType.X64
    assert request.env_type == EnvType.CLEAN
    assert request.obj_ext_browser == Browser.CHROME
    assert request.obj_ext_startfolder == StartFolder.TEMP
    assert request.opt_privacy_type == PrivacyType.BYLINK


def test_url_analysis_request() -> None:
    """Test URL analysis request."""
    request = URLAnalysisRequest(
        obj_url=HttpUrl("https://example.com"),
        file=None,
        task_rerun_uuid=None,
        env_os=OSType.LINUX,
        env_version=LinuxVersion.UBUNTU_22_04_2,
        env_bitness=BitnessType.X64,
        env_type=EnvType.OFFICE,
        env_locale=None,
        obj_ext_cmd=None,
        obj_ext_useragent=None,
        obj_ext_elevateprompt=None,
        obj_force_elevation=None,
        user_tags=None,
    )

    assert request.obj_type == ObjectType.URL
    assert str(request.obj_url).rstrip("/") == "https://example.com"
    assert request.env_os == OSType.LINUX
    assert request.env_version == LinuxVersion.UBUNTU_22_04_2
    assert request.env_bitness == BitnessType.X64
    assert request.env_type == EnvType.OFFICE


def test_rerun_analysis_request() -> None:
    """Test rerun analysis request."""
    request = RerunAnalysisRequest(
        task_rerun_uuid="test123",
        file=None,
        obj_url=None,
        env_os=OSType.WINDOWS,
        env_version=WindowsVersion.WIN10,
        env_bitness=BitnessType.X64,
        env_type=EnvType.CLEAN,
        env_locale=None,
        obj_ext_cmd=None,
        obj_ext_useragent=None,
        obj_ext_elevateprompt=None,
        obj_force_elevation=None,
        user_tags=None,
    )

    assert request.obj_type == ObjectType.RERUN
    assert request.task_rerun_uuid == "test123"
    assert request.env_os == OSType.WINDOWS
    assert request.env_version == WindowsVersion.WIN10
    assert request.env_bitness == BitnessType.X64
    assert request.env_type == EnvType.CLEAN
