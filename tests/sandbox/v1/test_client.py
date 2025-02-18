"""Tests for Sandbox API v1 client."""

import json
from datetime import datetime
from typing import Any, Dict

import pytest
import respx
from httpx import Response

from anyrun.exceptions import APIError
from anyrun.sandbox.v1.models.analysis import (
    BitnessType,
    Browser,
    EnvType,
    ObjectType,
    OSType,
    PrivacyType,
    StartFolder,
)


def json_serial(obj: Any) -> str:
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


async def test_analyze_file(mock_api: pytest.fixture, sandbox_client: pytest.fixture) -> None:
    """Test file analysis."""
    task_id = "test-task-id"
    mock_api.post("https://api.any.run/v1/analysis").mock(
        return_value=Response(
            200,
            json={
                "error": False,
                "data": {"taskid": task_id},
            },
        )
    )

    response = await sandbox_client.analyze_file(
        file=b"test content",
        env_os=OSType.WINDOWS,
        env_version="10",
        env_bitness=BitnessType.X64,
        env_type=EnvType.COMPLETE,
        obj_ext_browser=Browser.EDGE,
        obj_ext_startfolder=StartFolder.TEMP,
        opt_privacy_type=PrivacyType.BYLINK,
    )

    assert response.error is False
    assert response.data.taskid == task_id


async def test_analyze_url(mock_api: pytest.fixture, sandbox_client: pytest.fixture) -> None:
    """Test URL analysis."""
    task_id = "test-task-id"
    mock_api.post("https://api.any.run/v1/analysis").mock(
        return_value=Response(
            200,
            json={
                "error": False,
                "data": {"taskid": task_id},
            },
        )
    )

    response = await sandbox_client.analyze_url(
        url="https://example.com",
        env_os=OSType.LINUX,
        env_version="22.04.2",
        env_bitness=BitnessType.X64,
        env_type=EnvType.OFFICE,
    )

    assert response.error is False
    assert response.data.taskid == task_id


async def test_get_analysis(mock_api: pytest.fixture, sandbox_client: pytest.fixture) -> None:
    """Test getting analysis result."""
    task_id = "test-task-id"
    mock_api.get(f"https://api.any.run/v1/analysis/{task_id}").mock(
        return_value=Response(
            200,
            json={
                "error": False,
                "data": {
                    "task_id": task_id,
                    "status": "completed",
                    "completed": True,
                },
            },
        )
    )

    response = await sandbox_client.get_analysis(task_id)
    assert response.error is False
    assert response.data.task_id == task_id
    assert response.data.status == "completed"
    assert response.data.completed is True


async def test_list_analyses(mock_api: pytest.fixture, sandbox_client: pytest.fixture) -> None:
    """Test listing analyses."""
    mock_api.get("https://api.any.run/v1/analysis/list").mock(
        return_value=Response(
            200,
            json={
                "error": False,
                "data": {
                    "tasks": [
                        {
                            "uuid": "test-uuid",
                            "verdict": "No threats detected",
                            "date": "2024-02-18T00:00:00Z",
                            "tags": [],
                            "hashes": {
                                "md5": "d41d8cd98f00b204e9800998ecf8427e",
                                "sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
                                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                                "ssdeep": "3::",
                            },
                        }
                    ]
                },
            },
        )
    )

    response = await sandbox_client.list_analyses(limit=5)
    assert response.error is False
    assert len(response.data.tasks) == 1
    assert response.data.tasks[0].uuid == "test-uuid"


async def test_get_environment(mock_api: pytest.fixture, sandbox_client: pytest.fixture) -> None:
    """Test getting environment information."""
    mock_api.get("https://api.any.run/v1/environments").mock(
        return_value=Response(
            200,
            json={
                "error": False,
                "data": {
                    "environments": [
                        {
                            "os": "windows",
                            "software": {
                                "ie": {},
                                "upps": [],
                                "apps": [],
                            },
                            "bitness": 64,
                            "type": "complete",
                            "version": "10",
                        }
                    ]
                },
            },
        )
    )

    response = await sandbox_client.get_environment()
    assert response.error is False
    assert len(response.data.environments) == 1
    assert response.data.environments[0].os == "windows"


async def test_user_info(mock_api: pytest.fixture, sandbox_client: pytest.fixture) -> None:
    """Test getting user information."""
    mock_api.get("https://api.any.run/v1/user").mock(
        return_value=Response(
            200,
            json={
                "error": False,
                "data": {
                    "limits": {
                        "web": {"max_time": 3600},
                        "api": {"max_requests": 1000},
                        "parallels": {"max_tasks": 5},
                    }
                },
            },
        )
    )

    response = await sandbox_client.user_info()
    assert response.error is False
    assert response.data.limits.web["max_time"] == 3600


async def test_get_user_presets(mock_api: pytest.fixture, sandbox_client: pytest.fixture) -> None:
    """Test getting user presets."""
    mock_api.get("https://api.any.run/v1/user/presets").mock(
        return_value=Response(
            200,
            json=[
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
            ],
        )
    )

    response = await sandbox_client.get_user_presets()
    assert response.error is False
    assert len(response.data) == 1
    assert response.data[0].name == "Test Preset"


async def test_add_analysis_time(mock_api: pytest.fixture, sandbox_client: pytest.fixture) -> None:
    """Test adding time to analysis."""
    task_id = "test-task-id"
    mock_api.patch(f"https://api.any.run/v1/analysis/{task_id}/time/add").mock(
        return_value=Response(
            200,
            json={
                "error": False,
                "message": "Add time in task successful",
            },
        )
    )

    response = await sandbox_client.add_analysis_time(task_id)
    assert response.error is False
    assert response.message == "Add time in task successful"


async def test_stop_analysis(mock_api: pytest.fixture, sandbox_client: pytest.fixture) -> None:
    """Test stopping analysis."""
    task_id = "test-task-id"
    mock_api.patch(f"https://api.any.run/v1/analysis/{task_id}/stop").mock(
        return_value=Response(
            200,
            json={
                "error": False,
                "message": "Stop task successful",
            },
        )
    )

    response = await sandbox_client.stop_analysis(task_id)
    assert response.error is False
    assert response.message == "Stop task successful"


async def test_delete_analysis(mock_api: pytest.fixture, sandbox_client: pytest.fixture) -> None:
    """Test deleting analysis."""
    task_id = "test-task-id"
    mock_api.delete(f"https://api.any.run/v1/analysis/{task_id}").mock(
        return_value=Response(
            200,
            json={
                "error": False,
                "message": "Delete task successful",
            },
        )
    )

    response = await sandbox_client.delete_analysis(task_id)
    assert response.error is False
    assert response.message == "Delete task successful"


async def test_get_analysis_monitor(mock_api: pytest.fixture, sandbox_client: pytest.fixture) -> None:
    """Test getting analysis monitor data."""
    task_id = "test-task-id"
    mock_api.get(f"https://api.any.run/v1/analysis/{task_id}/monitor").mock(
        return_value=Response(
            200,
            json={
                "task": {
                    "uuid": task_id,
                    "status": 50,
                    "remaining": 300,
                },
                "completed": False,
                "error": False,
            },
        )
    )

    response = await sandbox_client.get_analysis_monitor(task_id)
    assert response["task"]["uuid"] == task_id
    assert response["task"]["status"] == 50
    assert response["completed"] is False 