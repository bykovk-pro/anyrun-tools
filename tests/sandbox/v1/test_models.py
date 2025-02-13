"""Tests for Sandbox API v1 models."""

import pytest
from pydantic import HttpUrl, ValidationError

from anyrun.sandbox.v1.models.analysis import (
    AnalysisListRequest,
    AnalysisListResponse,
    AnalysisRequest,
    AnalysisResponse,
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
from anyrun.sandbox.v1.models.environment import EnvironmentResponse
from anyrun.sandbox.v1.models.user import (
    UserInfoRequest,
    UserInfoResponse,
    UserPresetsResponse,
)


def test_analysis_request_validation() -> None:
    """Test analysis request validation."""
    # Valid file analysis request
    request = AnalysisRequest(
        obj_type=ObjectType.FILE,
        file=b"test content",
        env_os=OSType.WINDOWS,
        env_version=WindowsVersion.WIN10,
        env_bitness=BitnessType.X64,
        env_type=EnvType.CLEAN,
        obj_ext_browser=Browser.CHROME,
        obj_ext_startfolder=StartFolder.TEMP,
        opt_privacy_type=PrivacyType.BYLINK,
        obj_url=None,
        task_rerun_uuid=None,
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

    # Valid URL analysis request
    request = AnalysisRequest(
        obj_type=ObjectType.URL,
        obj_url=HttpUrl("https://example.com"),
        env_os=OSType.LINUX,
        env_version=LinuxVersion.UBUNTU_22_04_2,
        env_bitness=BitnessType.X64,
        env_type=EnvType.OFFICE,
        file=None,
        task_rerun_uuid=None,
        env_locale=None,
        obj_ext_cmd=None,
        obj_ext_useragent=None,
        obj_ext_elevateprompt=None,
        obj_force_elevation=None,
        user_tags=None,
    )
    assert request.obj_type == ObjectType.URL
    # Pydantic's HttpUrl automatically adds trailing slash, so we need to check the host part only
    assert str(request.obj_url).rstrip("/") == "https://example.com"

    # Invalid requests
    with pytest.raises(ValidationError):
        # Missing required file
        AnalysisRequest(
            obj_type=ObjectType.FILE,
            env_os=OSType.WINDOWS,
            env_version=WindowsVersion.WIN10,
            env_bitness=BitnessType.X64,
            env_type=EnvType.CLEAN,
            file=None,
            obj_url=None,
            task_rerun_uuid=None,
            env_locale=None,
            obj_ext_cmd=None,
            obj_ext_useragent=None,
            obj_ext_elevateprompt=None,
            obj_force_elevation=None,
            user_tags=None,
        )

    with pytest.raises(ValidationError):
        # Missing required URL
        AnalysisRequest(
            obj_type=ObjectType.URL,
            env_os=OSType.LINUX,
            env_version=LinuxVersion.UBUNTU_22_04_2,
            env_bitness=BitnessType.X64,
            env_type=EnvType.OFFICE,
            file=None,
            obj_url=None,
            task_rerun_uuid=None,
            env_locale=None,
            obj_ext_cmd=None,
            obj_ext_useragent=None,
            obj_ext_elevateprompt=None,
            obj_force_elevation=None,
            user_tags=None,
        )

    with pytest.raises(ValidationError):
        # Invalid OS version for Linux
        AnalysisRequest(
            obj_type=ObjectType.URL,
            obj_url=HttpUrl("https://example.com"),
            env_os=OSType.LINUX,
            env_version=WindowsVersion.WIN10,
            env_bitness=BitnessType.X64,
            env_type=EnvType.OFFICE,
            file=None,
            task_rerun_uuid=None,
            env_locale=None,
            obj_ext_cmd=None,
            obj_ext_useragent=None,
            obj_ext_elevateprompt=None,
            obj_force_elevation=None,
            user_tags=None,
        )

    with pytest.raises(ValidationError):
        # Invalid browser for Linux
        AnalysisRequest(
            obj_type=ObjectType.URL,
            obj_url=HttpUrl("https://example.com"),
            env_os=OSType.LINUX,
            env_version=LinuxVersion.UBUNTU_22_04_2,
            env_bitness=BitnessType.X64,
            env_type=EnvType.OFFICE,
            obj_ext_browser=Browser.IE,
            file=None,
            task_rerun_uuid=None,
            env_locale=None,
            obj_ext_cmd=None,
            obj_ext_useragent=None,
            obj_ext_elevateprompt=None,
            obj_force_elevation=None,
            user_tags=None,
        )


def test_analysis_response_validation() -> None:
    """Test analysis response validation."""
    # Valid response
    response = AnalysisResponse(
        error=False,
        data={"task_id": "test123", "status": "queued"},
    )
    assert response.error is False
    assert response.data["task_id"] == "test123"

    # Invalid response - error should be boolean
    with pytest.raises(ValidationError):
        AnalysisResponse(error=False, data="not_a_dict")  # type: ignore[arg-type]

    # Invalid response - data should be a dict
    with pytest.raises(ValidationError):
        AnalysisResponse(error=False, data="not_a_dict")  # type: ignore[arg-type]


def test_analysis_list_request_validation() -> None:
    """Test analysis list request validation."""
    # Valid request
    request = AnalysisListRequest(
        team=True,
        skip=10,
        limit=50,
    )
    assert request.team is True
    assert request.skip == 10
    assert request.limit == 50

    # Invalid request - skip should be >= 0
    with pytest.raises(ValidationError):
        AnalysisListRequest(skip=-1)

    # Invalid request - limit should be between 1 and 100
    with pytest.raises(ValidationError):
        AnalysisListRequest(limit=0)

    with pytest.raises(ValidationError):
        AnalysisListRequest(limit=101)


def test_analysis_list_response_validation() -> None:
    """Test analysis list response validation."""
    # Valid response
    response = AnalysisListResponse(
        error=False,
        data={"items": [{"task_id": "test123", "status": "completed"}], "total": 1},
    )
    assert response.error is False
    assert len(response.data["items"]) == 1
    assert response.data["total"] == 1

    # Invalid response - data should be a dict
    with pytest.raises(ValidationError):
        AnalysisListResponse(error=False, data="not_a_dict")  # type: ignore[arg-type]


def test_environment_response_validation() -> None:
    """Test environment response validation."""
    # Valid response
    response = EnvironmentResponse(
        error=False,
        data={
            "windows": {"versions": ["7", "10", "11"], "bitness": ["32", "64"]},
            "linux": {"versions": ["22.04.2"], "bitness": ["64"]},
        },
    )
    assert response.error is False
    assert "windows" in response.data
    assert "linux" in response.data

    # Invalid response - data should be a dict
    with pytest.raises(ValidationError):
        EnvironmentResponse(error=False, data="not_a_dict")  # type: ignore[arg-type]


def test_user_info_request_validation() -> None:
    """Test user info request validation."""
    # Valid request
    request = UserInfoRequest(team=True)
    assert request.team is True

    # Default values
    request = UserInfoRequest()
    assert request.team is False


def test_user_info_response_validation() -> None:
    """Test user info response validation."""
    # Valid response
    response = UserInfoResponse(
        error=False,
        data={"name": "test", "email": "test@example.com"},
    )
    assert response.error is False
    assert response.data["name"] == "test"

    # Invalid response - data should be a dict
    with pytest.raises(ValidationError):
        UserInfoResponse(error=False, data="not_a_dict")  # type: ignore[arg-type]


def test_user_presets_response_validation() -> None:
    """Test user presets response validation."""
    # Valid response
    response = UserPresetsResponse(
        error=False,
        data=[
            {
                "id": "preset1",
                "name": "Windows 10 x64",
                "settings": {"env_os": "windows", "env_version": "10"},
            },
            {
                "id": "preset2",
                "name": "Linux Ubuntu",
                "settings": {"env_os": "linux", "env_version": "22.04.2"},
            },
        ],
    )
    assert response.error is False
    assert len(response.data) == 2
    assert response.data[0]["id"] == "preset1"

    # Invalid response - data should be a list
    with pytest.raises(ValidationError):
        UserPresetsResponse(error=False, data="not_a_list")  # type: ignore[arg-type]

    # Invalid response - data should be a list of dicts with specific structure
    with pytest.raises(ValidationError):
        UserPresetsResponse(error=False, data=[{"invalid": "structure"}])
