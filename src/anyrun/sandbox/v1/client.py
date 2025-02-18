"""Sandbox API v1 client implementation."""

import json
import os
from typing import Any, AsyncGenerator, Dict, Union, cast

import httpx
from loguru import logger
from pydantic import HttpUrl

from ...exceptions import APIError, ValidationError
from ..base import BaseSandboxClient
from .endpoints import (
    ANALYSIS_ADD_TIME,
    ANALYSIS_CREATE,
    ANALYSIS_DELETE,
    ANALYSIS_GET,
    ANALYSIS_LIST,
    ANALYSIS_MONITOR,
    ANALYSIS_STOP,
    ENVIRONMENT_INFO,
    USER_INFO,
    USER_PRESETS,
)
from .models.analysis import (
    AddTimeResponse,
    AnalysisListRequest,
    AnalysisListResponse,
    AnalysisRequest,
    AnalysisResponse,
    DeleteAnalysisResponse,
    DownloadAnalysisRequest,
    FileAnalysisRequest,
    ObjectType,
    RerunAnalysisRequest,
    StopAnalysisResponse,
    URLAnalysisRequest,
)
from .models.environment import EnvironmentResponse
from .models.task_status_update import TaskStatusUpdateDto
from .models.user import UserInfoResponse, UserPresetsResponse


class SandboxClientV1(
    BaseSandboxClient[AnalysisResponse, AnalysisListResponse, EnvironmentResponse]
):
    """Sandbox API v1 client implementation."""

    def _get_endpoint(self, path: str) -> str:
        """Get versioned API endpoint.

        Args:
            path: API path

        Returns:
            str: Full API endpoint with version
        """
        return path

    def _get_file_content(self, file: Union[str, bytes]) -> bytes:
        """Get file content as bytes.

        Args:
            file: File content as string or bytes

        Returns:
            bytes: File content as bytes

        Raises:
            ValidationError: If file content is invalid
        """
        if isinstance(file, str):
            if os.path.isfile(file):
                with open(file, "rb") as f:
                    return f.read()
            return file.encode()
        return file

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response.

        Args:
            response: HTTP response

        Returns:
            Response data as dictionary

        Raises:
            APIError: If response is invalid
        """
        # Handle SSE responses
        if response.headers.get("content-type", "").startswith("text/event-stream"):
            try:
                # Extract data from SSE response
                result = json.loads(response.text.replace("data: ", ""))
                if not isinstance(result, dict):
                    raise APIError("SSE response data is not a dictionary")
                return result
            except json.JSONDecodeError:
                raise APIError(f"Invalid SSE JSON response: {response.text}")

        # Handle regular JSON responses
        try:
            data = response.json()
            if not isinstance(data, dict):
                raise APIError("Response data is not a dictionary")
            return data
        except json.JSONDecodeError:
            raise APIError(f"Invalid JSON response: {response.text}")

    async def analyze(self, **kwargs: Any) -> AnalysisResponse:
        """Submit new analysis.

        Args:
            **kwargs: Analysis parameters (see AnalysisRequest schema)

        Returns:
            AnalysisResponse: Analysis response

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request failed
        """
        try:
            request = AnalysisRequest(**kwargs)
            data = request.model_dump(exclude_none=True)  # Only include non-None fields

            # Convert enum values to strings
            for key, value in data.items():
                if hasattr(value, "value"):
                    data[key] = value.value

            logger.debug(f"Analysis request data: {data}")

            files = None
            if request.obj_type == ObjectType.FILE:
                if not request.file:
                    raise ValidationError("file is required for file analysis")
                # Handle file content as bytes
                filename = kwargs.get("filename", "malware.exe")
                file_content = self._get_file_content(request.file)
                files = {
                    "file": (
                        filename,
                        file_content,
                    )
                }

            client = await self._ensure_client()
            response = await client.post(
                self._get_endpoint(ANALYSIS_CREATE),
                headers=self._get_headers(),
                data=data,
                files=files,
            )

            logger.debug(f"API response status: {response.status_code}")
            logger.debug(f"API response headers: {response.headers}")
            logger.debug(f"API response text: {response.text}")

            result = await self._handle_response(response)
            return cast(AnalysisResponse, AnalysisResponse.model_validate(result))

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValidationError(f"Invalid analysis parameters: {str(e)}")
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            if isinstance(e, httpx.HTTPError):
                logger.error(f"HTTP error details: {str(e)}")
            raise APIError(f"Failed to submit analysis: {str(e)}")

    async def get_analysis(self, task_id: str) -> AnalysisResponse:
        """Get analysis information.

        Args:
            task_id: Analysis task ID

        Returns:
            AnalysisResponse: Analysis information

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.get(
            self._get_endpoint(ANALYSIS_GET.format(task_id=task_id)),
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return cast(AnalysisResponse, AnalysisResponse.model_validate(result))

    async def list_analyses(self, **kwargs: Any) -> AnalysisListResponse:
        """Get list of analyses.

        Args:
            **kwargs: List parameters (see AnalysisListRequest schema)

        Returns:
            AnalysisListResponse: List of analyses

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request failed
        """
        try:
            request = AnalysisListRequest(**kwargs)
            client = await self._ensure_client()
            response = await client.get(
                self._get_endpoint(ANALYSIS_LIST),
                headers=self._get_headers(),
                params=request.model_dump(exclude_unset=True),
            )

            result = await self._handle_response(response)
            return cast(AnalysisListResponse, AnalysisListResponse.model_validate(result))

        except ValidationError as e:
            raise ValidationError(f"Invalid list parameters: {str(e)}")
        except Exception as e:
            raise APIError(f"Failed to list analyses: {str(e)}")

    async def get_environment(self) -> EnvironmentResponse:
        """Get available environment information.

        Returns:
            EnvironmentResponse: Environment information

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.get(
            self._get_endpoint(ENVIRONMENT_INFO),
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return cast(EnvironmentResponse, EnvironmentResponse.model_validate(result))

    async def user_info(self) -> UserInfoResponse:
        """Get user information and limits.

        Returns:
            UserInfoResponse: User information and limits

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.get(
            self._get_endpoint(USER_INFO),
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return cast(UserInfoResponse, UserInfoResponse.model_validate(result))

    async def get_user_presets(self) -> UserPresetsResponse:
        """Get user presets.

        Returns:
            UserPresetsResponse: User presets

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.get(
            self._get_endpoint(USER_PRESETS),
            headers=self._get_headers(),
        )

        try:
            # Handle both array and wrapped response formats
            data = response.json()
            return UserPresetsResponse.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to get user presets. Status: {response.status_code}")
            logger.error(f"Response headers: {dict(response.headers)}")
            logger.error(f"Response text: {response.text}")
            raise APIError(f"Failed to get user presets: {str(e)}")

    async def add_analysis_time(self, task_id: str) -> AddTimeResponse:
        """Add time to running analysis.

        Args:
            task_id: Analysis task ID

        Returns:
            AddTimeResponse: Response data

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.patch(
            self._get_endpoint(ANALYSIS_ADD_TIME.format(task_id=task_id)),
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return cast(AddTimeResponse, AddTimeResponse.model_validate(result))

    async def stop_analysis(self, task_id: str) -> StopAnalysisResponse:
        """Stop running analysis.

        Args:
            task_id: Analysis task ID

        Returns:
            StopAnalysisResponse: Response data

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.patch(
            self._get_endpoint(ANALYSIS_STOP.format(task_id=task_id)),
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return cast(StopAnalysisResponse, StopAnalysisResponse.model_validate(result))

    async def delete_analysis(self, task_id: str) -> DeleteAnalysisResponse:
        """Delete analysis.

        Args:
            task_id: Analysis task ID

        Returns:
            DeleteAnalysisResponse: Response data

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.delete(
            self._get_endpoint(ANALYSIS_DELETE.format(task_id=task_id)),
            headers=self._get_headers(),
        )

        result = await self._handle_response(response)
        return cast(DeleteAnalysisResponse, DeleteAnalysisResponse.model_validate(result))

    async def analyze_file(self, file: Union[str, bytes], **kwargs: Any) -> AnalysisResponse:
        """Submit file for analysis.

        Args:
            file: File content as string or bytes
            **kwargs: Additional analysis parameters

        Returns:
            AnalysisResponse: Analysis response

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request failed
        """
        kwargs["obj_type"] = ObjectType.FILE
        kwargs["file"] = self._get_file_content(file)
        request = FileAnalysisRequest(**kwargs)
        return await self.analyze(**request.model_dump())

    async def analyze_url(self, url: Union[str, HttpUrl], **kwargs: Any) -> AnalysisResponse:
        """Submit URL for analysis.

        Args:
            url: Target URL
            **kwargs: Additional analysis parameters

        Returns:
            AnalysisResponse: Analysis response

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request failed
        """
        kwargs["obj_type"] = ObjectType.URL
        kwargs["obj_url"] = str(url)
        request = URLAnalysisRequest(**kwargs)
        return await self.analyze(**request.model_dump())

    async def rerun_analysis(self, task_uuid: str, **kwargs: Any) -> AnalysisResponse:
        """Rerun existing analysis.

        Args:
            task_uuid: Task UUID to rerun
            **kwargs: Additional analysis parameters

        Returns:
            AnalysisResponse: Analysis response

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request failed
        """
        kwargs["obj_type"] = ObjectType.RERUN
        kwargs["task_rerun_uuid"] = task_uuid
        request = RerunAnalysisRequest(**kwargs)
        return await self.analyze(**request.model_dump())

    async def get_analysis_monitor(self, task_id: str) -> Dict[str, Any]:
        """Get analysis monitor data.

        Args:
            task_id: Analysis task ID

        Returns:
            Dict[str, Any]: Monitor data

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        response = await client.get(
            self._get_endpoint(ANALYSIS_MONITOR.format(task_id=task_id)),
            headers=self._get_headers(),
        )

        return await self._handle_response(response)

    async def get_analysis_status_stream(
        self, task_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Get analysis status stream.

        Args:
            task_id: Analysis task ID

        Yields:
            Dict[str, Any]: Status update

        Raises:
            APIError: If API request failed
        """
        client = await self._ensure_client()
        async with client.stream(
            "GET",
            self._get_endpoint(ANALYSIS_MONITOR.format(task_id=task_id)),
            headers=self._get_headers(),
        ) as response:
            if response.status_code != 200:
                raise APIError(f"Failed to get analysis status: {response.status_code}")

            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                if not line.startswith("data: "):
                    continue
                try:
                    data = json.loads(line[6:])  # Remove "data: " prefix
                    if isinstance(data, dict):
                        # Convert to model and back to dict to validate and normalize data
                        update = TaskStatusUpdateDto.model_validate(data)
                        yield update.model_dump()
                except json.JSONDecodeError as e:
                    raise APIError(f"Invalid SSE JSON response: {line}") from e
                except Exception as e:
                    raise APIError(f"Error processing SSE response: {str(e)}") from e

    async def analyze_download(self, url: Union[str, HttpUrl], **kwargs: Any) -> AnalysisResponse:
        """Submit URL for download and analysis.

        Args:
            url: URL to download and analyze
            **kwargs: Additional analysis parameters

        Returns:
            AnalysisResponse: Analysis response

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request failed
        """
        kwargs["obj_type"] = ObjectType.DOWNLOAD
        kwargs["obj_url"] = str(url)
        request = DownloadAnalysisRequest(**kwargs)
        return await self.analyze(**request.model_dump())
