"""Tests for Sandbox API v1 endpoints."""

import httpx
import pytest
import respx

from anyrun.sandbox.v1.endpoints import (
    ANALYSIS_CREATE,
    ANALYSIS_GET,
    ANALYSIS_LIST,
    ANALYSIS_MONITOR,
    ANALYSIS_STATUS,
    ENVIRONMENT_INFO,
)
from anyrun.sandbox.v1.models.analysis import (
    BitnessType,
    EnvType,
    OSType,
    WindowsVersion,
)


def test_endpoints_format() -> None:
    """Test that all endpoints start with a forward slash."""
    endpoints = [
        ANALYSIS_CREATE,
        ANALYSIS_GET,
        ANALYSIS_LIST,
        ANALYSIS_STATUS,
        ANALYSIS_MONITOR,
        ENVIRONMENT_INFO,
    ]
    for endpoint in endpoints:
        assert endpoint.startswith("/")


def test_analysis_endpoints() -> None:
    """Test analysis endpoints format."""
    task_id = "test123"
    assert ANALYSIS_GET.format(task_id=task_id) == f"/v1/analysis/{task_id}"
    assert ANALYSIS_STATUS.format(task_id=task_id) == f"/v1/analysis/{task_id}/status"
    assert ANALYSIS_MONITOR.format(task_id=task_id) == f"/v1/analysis/{task_id}/monitor"


def test_environment_endpoints() -> None:
    """Test environment endpoints format."""
    assert ENVIRONMENT_INFO == "/v1/environment"


def test_user_endpoints() -> None:
    """Test user endpoints format."""
    assert ANALYSIS_LIST == "/v1/analysis"


@pytest.mark.asyncio
async def test_analysis_create_endpoint(
    mock_api: respx.Router, client: httpx.AsyncClient
) -> None:
    """Test analysis create endpoint."""
    mock_api.post(ANALYSIS_CREATE).mock(
        return_value=httpx.Response(
            status_code=200,
            json={"error": False, "data": {"task_id": "test123", "status": "queued"}},
        )
    )

    response = await client.sandbox.analyze_file(
        file=b"test content",
        env_os=OSType.WINDOWS,
        env_version=WindowsVersion.WIN10,
        env_bitness=BitnessType.X64,
        env_type=EnvType.CLEAN,
    )
    assert response.error is False
    assert response.data["task_id"] == "test123"
    assert response.data["status"] == "queued"


@pytest.mark.asyncio
async def test_analysis_get_endpoint(
    mock_api: respx.Router, client: httpx.AsyncClient
) -> None:
    """Test analysis get endpoint."""
    task_id = "test123"
    endpoint = ANALYSIS_GET.format(task_id=task_id)

    mock_api.get(endpoint).mock(
        return_value=httpx.Response(
            status_code=200,
            json={"error": False, "data": {"task_id": task_id, "status": "completed"}},
        )
    )

    response = await client.sandbox.get_analysis(task_id)
    assert response.error is False
    assert response.data["task_id"] == task_id
    assert response.data["status"] == "completed"


@pytest.mark.asyncio
async def test_analysis_list_endpoint(
    mock_api: respx.Router, client: httpx.AsyncClient
) -> None:
    """Test analysis list endpoint."""
    mock_api.get(ANALYSIS_LIST).mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "error": False,
                "data": {
                    "items": [{"task_id": "test123", "status": "completed"}],
                    "total": 1,
                },
            },
        )
    )

    response = await client.sandbox.list_analyses()
    assert response.error is False
    assert len(response.data["items"]) == 1
    assert response.data["items"][0]["task_id"] == "test123"
    assert response.data["total"] == 1


@pytest.mark.asyncio
async def test_analysis_status_endpoint(
    mock_api: respx.Router, client: httpx.AsyncClient
) -> None:
    """Test analysis status endpoint."""
    task_id = "test123"
    endpoint = ANALYSIS_STATUS.format(task_id=task_id)

    mock_api.get(endpoint).mock(
        return_value=httpx.Response(
            status_code=200,
            json={"error": False, "data": {"status": "running", "progress": 50}},
        )
    )

    response = await client.sandbox.get_analysis_status(task_id)
    assert response.error is False
    assert response.data["status"] == "running"
    assert response.data["progress"] == 50


@pytest.mark.asyncio
async def test_analysis_monitor_endpoint(
    mock_api: respx.Router, client: httpx.AsyncClient
) -> None:
    """Test analysis monitor endpoint."""
    task_id = "test123"
    endpoint = ANALYSIS_MONITOR.format(task_id=task_id)

    mock_api.get(endpoint).mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "error": False,
                "data": {"process": {"pid": 1234, "name": "test.exe"}},
            },
        )
    )

    response = await client.sandbox.get_analysis_monitor(task_id)
    assert response.error is False
    assert response.data["process"]["pid"] == 1234
    assert response.data["process"]["name"] == "test.exe"


@pytest.mark.asyncio
async def test_environment_info_endpoint(
    mock_api: respx.Router, client: httpx.AsyncClient
) -> None:
    """Test environment info endpoint."""
    mock_api.get(ENVIRONMENT_INFO).mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "error": False,
                "data": {
                    "windows": {"versions": ["7", "10", "11"], "bitness": ["32", "64"]},
                    "linux": {"versions": ["22.04.2"], "bitness": ["64"]},
                },
            },
        )
    )

    response = await client.sandbox.get_environment()
    assert response.error is False
    assert "windows" in response.data
    assert "linux" in response.data
