"""Tests for Sandbox API v1 models."""

import pytest
from pydantic import HttpUrl, ValidationError
from datetime import datetime

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
    AnalysisData,
    AnalysisListData,
    AnalysisListItem,
)
from anyrun.sandbox.v1.models.environment import EnvironmentResponse
from anyrun.sandbox.v1.models.user import (
    UserInfoRequest,
    UserInfoResponse,
    UserPresetsResponse,
    UserPreset,
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
        data=AnalysisData(task_id="test123", status="queued"),
        message=None
    )
    assert response.error is False
    assert response.data.task_id == "test123"
    assert response.data.status == "queued"

    # Invalid response - data should be a dict
    with pytest.raises(ValidationError):
        AnalysisResponse(error=False, data=AnalysisData(invalid="data"), message=None)

    # Invalid response - missing required fields
    with pytest.raises(ValidationError):
        AnalysisResponse(error=False, data=AnalysisData(), message=None)


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
        data=AnalysisListData(
            tasks=[AnalysisListItem(
                uuid="test123",
                verdict="No threats detected",
                name="test.exe",
                related=None,
                pcap=None,
                file=None,
                json=None,
                misp=None,
                date=None,
                tags=[],
                hashes=None
            )]
        ),
        message=None
    )
    assert response.error is False
    assert len(response.data.tasks) == 1
    assert response.data.tasks[0].uuid == "test123"

    # Invalid response - data should be valid
    with pytest.raises(ValidationError):
        AnalysisListResponse(
            error=False,
            data=AnalysisListData(tasks=[]),
            message=None
        )

    # Invalid response - missing required fields
    with pytest.raises(ValidationError):
        AnalysisListResponse(
            error=False,
            data=AnalysisListData(tasks=None),
            message=None
        )


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
        EnvironmentResponse(error=False, data={"invalid": "data"})

    # Invalid response - missing required fields
    with pytest.raises(ValidationError):
        EnvironmentResponse(error=False, data={})


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
        UserInfoResponse(error=False, data={})

    # Invalid response - missing required fields
    with pytest.raises(ValidationError):
        UserInfoResponse(error=False, data={"invalid": "data"})


def test_user_presets_response_validation() -> None:
    """Test user presets response validation."""
    # Valid response
    preset = UserPreset(
        _id="preset1",
        name="Test Preset",
        userId="user1",
        userPlanName="pro",
        createTime=datetime.now(),
        os="windows",
        version="10",
        bitness=64,
        type="clean",
        browser="Google Chrome",
        locale="en-US",
        location="desktop",
        netConnected=True,
        network="default",
        fakenet=False,
        mitm=False,
        netviator=False,
        vpn=False,
        openVPN="",
        torGeo="",
        residentialProxy=False,
        residentialProxyGeo="",
        timeout=300,
        privacy="bylink",
        hide_source=False,
        extension=False,
        autoclicker=False,
        el=False,
        noControls=False,
        expirationTime=datetime.now().isoformat(),
        expirationTimeSelected=False,
    )
    response = UserPresetsResponse(
        error=False,
        data=[preset],
    )
    assert response.error is False
    assert len(response.data) == 1

    # Invalid response - data should be a list
    with pytest.raises(ValidationError):
        UserPresetsResponse(error=False, data=[])

    # Invalid response - missing required fields
    with pytest.raises(ValidationError):
        UserPresetsResponse(error=False, data=[])


def test_user_preset_validation() -> None:
    """Test user preset validation."""
    # Valid preset
    preset = UserPreset(
        _id="preset1",
        name="Test Preset",
        userId="user1",
        userPlanName="pro",
        createTime=datetime.now(),
        os="windows",
        version="10",
        bitness=64,
        type="clean",
        browser="Google Chrome",
        locale="en-US",
        location="desktop",
        netConnected=True,
        network="default",
        fakenet=False,
        mitm=False,
        netviator=False,
        vpn=False,
        openVPN="",
        torGeo="",
        residentialProxy=False,
        residentialProxyGeo="",
        timeout=300,
        privacy="bylink",
        hide_source=False,
        extension=False,
        autoclicker=False,
        el=False,
        noControls=False,
        expirationTime=datetime.now().isoformat(),
        expirationTimeSelected=False,
    )
    assert preset.id == "preset1"
    assert preset.name == "Test Preset"

    # Invalid preset - missing required fields
    with pytest.raises(ValidationError):
        UserPreset(
            _id="",
            name="",
            userId="",
            userPlanName="",
            createTime=datetime.now(),
            os="",
            version="",
            bitness=0,
            type="",
            browser="",
            locale="",
            location="",
            netConnected=False,
            network="",
            fakenet=False,
            mitm=False,
            netviator=False,
            vpn=False,
            openVPN="",
            torGeo="",
            residentialProxy=False,
            residentialProxyGeo="",
            timeout=0,
            privacy="",
            hide_source=False,
            extension=False,
            autoclicker=False,
            el=False,
            noControls=False,
            expirationTime="",
            expirationTimeSelected=False,
        )
