"""Tests for Sandbox API client."""

from typing import Any, Dict, Optional, cast

import httpx
import pytest
import respx
from pydantic import HttpUrl

from anyrun.sandbox.v1.client import SandboxClientV1 as SandboxClient
from anyrun.sandbox.v1.models.analysis import (
    AnalysisListResponse,
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


@pytest.mark.asyncio
async def test_sandbox_client_initialization() -> None:
    """Test sandbox client initialization."""
    client = SandboxClient(
        api_key="test_key",
        base_url=HttpUrl("https://api.any.run"),
        timeout=30,
        verify_ssl=True,
        proxies=None,
        user_agent=None,
        headers={},
    )
    assert client.api_key == "test_key"
    assert str(client.base_url) == "https://api.any.run"


@pytest.mark.asyncio
async def test_sandbox_analyze_file(mock_api: respx.Router) -> None:
    """Test sandbox analyze file."""
    mock_api.post("/v1/analysis").mock(
        return_value=httpx.Response(
            200,
            json={
                "error": False,
                "data": {"task_id": "test123", "status": "queued"},
            },
        )
    )

    client = SandboxClient(api_key="test_key")
    response = await client.analyze(
        obj_type=ObjectType.FILE,
        file=b"test content",
        env_os=OSType.WINDOWS,
        env_version=WindowsVersion.WIN10,
        env_bitness=BitnessType.X64,
        env_type=EnvType.CLEAN,
        obj_ext_browser=Browser.CHROME,
        obj_ext_startfolder=StartFolder.TEMP,
        opt_privacy_type=PrivacyType.BYLINK,
    )

    assert isinstance(response, AnalysisResponse)
    assert response.data["task_id"] == "test123"
    assert response.data["status"] == "queued"


@pytest.mark.asyncio
async def test_sandbox_analyze_url(mock_api: respx.Router) -> None:
    """Test sandbox analyze URL."""
    mock_api.post("/v1/analysis").mock(
        return_value=httpx.Response(
            200,
            json={
                "error": False,
                "data": {"task_id": "test123", "status": "queued"},
            },
        )
    )

    client = SandboxClient(api_key="test_key")
    response = await client.analyze(
        obj_type=ObjectType.URL,
        obj_url=HttpUrl("https://example.com"),
        env_os=OSType.LINUX,
        env_version=LinuxVersion.UBUNTU_22_04_2,
        env_bitness=BitnessType.X64,
        env_type=EnvType.OFFICE,
    )

    assert isinstance(response, AnalysisResponse)
    assert response.data["task_id"] == "test123"
    assert response.data["status"] == "queued"


@pytest.mark.asyncio
async def test_sandbox_get_analysis(mock_api: respx.Router) -> None:
    """Test sandbox get analysis."""
    mock_api.get("/v1/analysis/test123").mock(
        return_value=httpx.Response(
            200,
            json={
                "error": False,
                "data": {"task_id": "test123", "status": "completed"},
            },
        )
    )

    client = SandboxClient(api_key="test_key")
    response = await client.get_analysis("test123")

    assert isinstance(response, AnalysisResponse)
    assert response.data["task_id"] == "test123"
    assert response.data["status"] == "completed"


@pytest.mark.asyncio
async def test_sandbox_list_analyses(mock_api: respx.Router) -> None:
    """Test sandbox list analyses."""
    mock_api.get("/v1/analysis").mock(
        return_value=httpx.Response(
            200,
            json={
                "error": False,
                "data": {
                    "items": [{"task_id": "test123", "status": "completed"}],
                    "total": 1,
                },
            },
        )
    )

    client = SandboxClient(api_key="test_key")
    response = await client.list_analyses(team=True, skip=0, limit=25)

    assert isinstance(response, AnalysisListResponse)
    assert len(response.data["items"]) == 1
    assert response.data["items"][0]["task_id"] == "test123"
    assert response.data["total"] == 1


@pytest.mark.asyncio
async def test_sandbox_get_analysis_status(mock_api: respx.Router) -> None:
    """Test sandbox get analysis status."""
    mock_api.get("/v1/analysis/monitor/test123").mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "error": False,
                    "data": {
                        "task": {"status": 10, "message": "Queued"},
                        "completed": False,
                    },
                },
            ),
            httpx.Response(
                200,
                json={
                    "error": False,
                    "data": {
                        "task": {"status": 50, "message": "Running"},
                        "completed": False,
                    },
                },
            ),
            httpx.Response(
                200,
                json={
                    "error": False,
                    "data": {
                        "task": {"status": 100, "message": "Completed"},
                        "completed": True,
                    },
                },
            ),
        ]
    )

    client = SandboxClient(api_key="test_key")
    status_updates = []
    async for update in client.get_analysis_status_stream("test123"):
        status_updates.append(update)

    assert len(status_updates) == 3
    assert status_updates[0]["task"]["status"] == 10
    assert status_updates[1]["task"]["status"] == 50
    assert status_updates[2]["task"]["status"] == 100
    assert status_updates[2]["completed"] is True


@pytest.mark.asyncio
async def test_sandbox_get_analysis_status_error(mock_api: respx.Router) -> None:
    """Test sandbox get analysis status with error."""
    mock_api.get("/v1/analysis/monitor/test123").mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "error": False,
                    "data": {
                        "task": {"status": 10, "message": "Queued"},
                        "completed": False,
                    },
                },
            ),
            httpx.Response(
                200,
                json={
                    "error": True,
                    "data": {
                        "task": {"status": -1, "message": "Error"},
                        "completed": True,
                    },
                },
            ),
        ]
    )

    client = SandboxClient(api_key="test_key")
    status_updates = []
    async for update in client.get_analysis_status_stream("test123"):
        status_updates.append(update)

    assert len(status_updates) == 2
    assert status_updates[0]["task"]["status"] == 10
    assert status_updates[1]["task"]["status"] == -1
    assert status_updates[1]["error"] is True


@pytest.mark.asyncio
async def test_sandbox_get_environment(mock_api: respx.Router) -> None:
    """Test sandbox get environment."""
    mock_api.get("/v1/environment").mock(
        return_value=httpx.Response(
            200,
            json={
                "error": False,
                "data": {
                    "windows": {"versions": ["7", "10", "11"], "bitness": ["32", "64"]},
                    "linux": {"versions": ["22.04.2"], "bitness": ["64"]},
                },
            },
        )
    )

    client = SandboxClient(api_key="test_key")
    response = await client.get_environment()

    assert isinstance(response, EnvironmentResponse)
    assert "windows" in response.data
    assert "linux" in response.data
    assert "7" in response.data["windows"]["versions"]
    assert "22.04.2" in response.data["linux"]["versions"]
