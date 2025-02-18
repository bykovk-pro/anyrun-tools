"""Tests for Sandbox API v1 models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from anyrun.sandbox.v1.models.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    BitnessType,
    Browser,
    EnvType,
    ObjectType,
    OSType,
    PrivacyType,
    StartFolder,
)
from anyrun.sandbox.v1.models.common import HashesApiDto, ThreatLevelText
from anyrun.sandbox.v1.models.environment import EnvironmentResponse
from anyrun.sandbox.v1.models.task_status_update import TaskStatusUpdateDto
from anyrun.sandbox.v1.models.user import UserInfoResponse, UserPresetsResponse


def test_analysis_request_validation() -> None:
    """Test analysis request validation."""
    # Test valid file analysis request
    request = AnalysisRequest(
        obj_type=ObjectType.FILE,
        file=b"test content",
        env_os=OSType.WINDOWS,
        env_version="10",
        env_bitness=BitnessType.X64,
        env_type=EnvType.COMPLETE,
        obj_ext_browser=Browser.EDGE,
        obj_ext_startfolder=StartFolder.TEMP,
        opt_privacy_type=PrivacyType.BYLINK,
    )
    assert request.obj_type == ObjectType.FILE
    assert request.file == b"test content"

    # Test valid URL analysis request
    request = AnalysisRequest(
        obj_type=ObjectType.URL,
        obj_url="https://example.com",
        env_os=OSType.LINUX,
        env_version="22.04.2",
        env_bitness=BitnessType.X64,
        env_type=EnvType.OFFICE,
    )
    assert request.obj_type == ObjectType.URL
    assert request.obj_url == "https://example.com"

    # Test invalid request (missing required fields)
    with pytest.raises(ValidationError):
        AnalysisRequest(obj_type=ObjectType.FILE)

    with pytest.raises(ValidationError):
        AnalysisRequest(obj_type=ObjectType.URL)


def test_analysis_response_validation() -> None:
    """Test analysis response validation."""
    response = AnalysisResponse(
        error=False,
        data={
            "taskid": "test-task-id",
            "status": "running",
            "completed": False,
        },
    )
    assert response.error is False
    assert response.data.taskid == "test-task-id"
    assert response.data.status == "running"
    assert response.data.completed is False


def test_environment_response_validation() -> None:
    """Test environment response validation."""
    response = EnvironmentResponse(
        error=False,
        data={
            "environments": [
                {
                    "os": "windows",
                    "software": {
                        "ie": {},
                        "upps": [],
                        "apps": [
                            {
                                "name": "Test App",
                                "version": "1.0",
                            }
                        ],
                    },
                    "bitness": 64,
                    "type": "complete",
                    "version": "10",
                }
            ]
        },
    )
    assert response.error is False
    assert len(response.data.environments) == 1
    assert response.data.environments[0].os == "windows"
    assert response.data.environments[0].bitness == 64


def test_task_status_update_validation() -> None:
    """Test task status update validation."""
    update = TaskStatusUpdateDto(
        task={
            "uuid": "test-uuid",
            "status": 50,
            "remaining": 300,
            "times": {
                "created": datetime.now(),
            },
            "public": {
                "maxAddedTimeReached": False,
                "objects": {
                    "names": {},
                    "hashes": {
                        "md5": "d41d8cd98f00b204e9800998ecf8427e",
                        "sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
                        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        "ssdeep": "3::",
                    },
                },
                "options": {
                    "private": PrivacyType.BYLINK,
                    "whitelist": [],
                    "mitm": False,
                    "fakenet": False,
                    "netviator": False,
                    "netConnected": True,
                    "network": "default",
                    "logger": "default",
                    "presentation": False,
                    "teamwork": False,
                    "reboots": False,
                    "onlyimportant": False,
                    "video": False,
                    "autoclicker": False,
                },
                "environment": {
                    "OS": {},
                    "software": [],
                },
            },
            "scores": {
                "specs": {},
                "verdict": {},
            },
            "actions": {},
        },
        completed=False,
        error=False,
    )
    assert update.task.uuid == "test-uuid"
    assert update.task.status == 50
    assert update.completed is False
    assert update.error is False


def test_user_info_response_validation() -> None:
    """Test user info response validation."""
    response = UserInfoResponse(
        error=False,
        data={
            "limits": {
                "web": {"max_time": 3600},
                "api": {"max_requests": 1000},
                "parallels": {"max_tasks": 5},
            }
        },
    )
    assert response.error is False
    assert response.data.limits.web["max_time"] == 3600
    assert response.data.limits.api["max_requests"] == 1000
    assert response.data.limits.parallels["max_tasks"] == 5


def test_user_presets_response_validation() -> None:
    """Test user presets response validation."""
    # Test direct list response
    response = UserPresetsResponse.model_validate([
        {
            "_id": "test-id",
            "name": "Test Preset",
            "userId": "user-id",
            "userPlanName": "basic",
            "createTime": "2024-02-18T00:00:00Z",
            "os": "Windows",
            "version": "10",
            "bitness": 64,
            "type": "complete",
            "browser": "Google Chrome",
            "locale": "en-US",
            "location": "desktop",
            "netConnected": True,
            "network": "default",
            "fakenet": False,
            "mitm": False,
            "netviator": False,
            "vpn": False,
            "openVPN": "",
            "torGeo": "",
            "residentialProxy": False,
            "residentialProxyGeo": "",
            "timeout": 60,
            "privacy": "bylink",
            "hide_source": False,
            "extension": False,
            "autoclicker": False,
            "el": False,
            "noControls": False,
            "expirationTime": "2024-02-19T00:00:00Z",
            "expirationTimeSelected": False,
        }
    ])
    assert len(response.data) == 1
    assert response.data[0].name == "Test Preset"
    assert response.error is False

    # Test wrapped response
    response = UserPresetsResponse.model_validate({
        "error": False,
        "data": [
            {
                "_id": "test-id",
                "name": "Test Preset",
                "userId": "user-id",
                "userPlanName": "basic",
                "createTime": "2024-02-18T00:00:00Z",
                "os": "Windows",
                "version": "10",
                "bitness": 64,
                "type": "complete",
                "browser": "Google Chrome",
                "locale": "en-US",
                "location": "desktop",
                "netConnected": True,
                "network": "default",
                "fakenet": False,
                "mitm": False,
                "netviator": False,
                "vpn": False,
                "openVPN": "",
                "torGeo": "",
                "residentialProxy": False,
                "residentialProxyGeo": "",
                "timeout": 60,
                "privacy": "bylink",
                "hide_source": False,
                "extension": False,
                "autoclicker": False,
                "el": False,
                "noControls": False,
                "expirationTime": "2024-02-19T00:00:00Z",
                "expirationTimeSelected": False,
            }
        ]
    })
    assert len(response.data) == 1
    assert response.data[0].name == "Test Preset"
    assert response.error is False 