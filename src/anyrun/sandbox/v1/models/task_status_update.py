"""Task status update models for Sandbox API v1."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from .common import HashesApiDto, PrivacyType


class TaskScoresDto(BaseModel):
    """Task scores model."""

    specs: Dict[str, bool] = Field(description="Task specifications")
    verdict: Dict[str, Any] = Field(description="Task verdict")


class TaskObjectDto(BaseModel):
    """Task object model."""

    names: Optional[Dict[str, str]] = Field(None, description="Object names")
    hashes: Optional[HashesApiDto] = Field(None, description="Object hashes")
    urls: Optional[Dict[str, str]] = Field(None, description="Object URLs")


class TaskOptionsDto(BaseModel):
    """Task options model."""

    private: PrivacyType = Field(description="Privacy level")
    whitelist: List[str] = Field(default=[], description="Whitelisted items")
    mitm: bool = Field(description="MITM status")
    fakenet: bool = Field(description="FakeNet status")
    openVPN: Optional[str] = Field(None, description="OpenVPN configuration")
    torGeo: Optional[str] = Field(None, description="TOR geography")
    netviator: bool = Field(description="Netviator status")
    netConnected: bool = Field(description="Network connection status")
    network: str = Field(description="Network type")
    logger: str = Field(description="Logger type")
    presentation: bool = Field(description="Presentation mode")
    teamwork: bool = Field(description="Team collaboration")
    reboots: bool = Field(description="System reboots")
    onlyimportant: bool = Field(description="Important events only")
    video: bool = Field(description="Video recording")
    locale: Optional[str] = Field(None, description="System locale")
    residentialProxyGeo: Optional[str] = Field(None, description="Residential proxy geography")
    residentialProxy: bool = Field(description="Residential proxy status")
    autoclickerDebugMode: Optional[bool] = Field(None, description="Autoclicker debug mode")
    autoclicker: bool = Field(description="Autoclicker status")
    chatGPT: Optional[bool] = Field(None, description="ChatGPT integration")


class TaskEnvironmentDto(BaseModel):
    """Task environment model."""

    OS: Dict[str, Any] = Field(description="Operating system information")
    software: List[Dict[str, Any]] = Field(default=[], description="Installed software")


class TaskPublicDto(BaseModel):
    """Task public information model."""

    maxAddedTimeReached: bool = Field(description="Maximum allowed task runtime reached")
    objects: TaskObjectDto = Field(description="Task objects information")
    options: TaskOptionsDto = Field(description="Task options")
    environment: TaskEnvironmentDto = Field(description="Task environment information")


class TaskTimesDto(BaseModel):
    """Task timing information."""

    created: Optional[datetime] = Field(None, description="Task creation time")
    started: Optional[datetime] = Field(None, description="Task start time")
    completed: Optional[datetime] = Field(None, description="Task completion time")
    addedTime: Optional[datetime] = Field(None, description="Time when additional time was added")


class TaskActionsDto(BaseModel):
    """Task actions model."""

    addTime: Optional[bool] = Field(None, description="Can add time")
    stop: Optional[bool] = Field(None, description="Can stop task")
    delete: Optional[bool] = Field(None, description="Can delete task")


class TaskStatusDto(BaseModel):
    """Task status model."""

    id: Optional[str] = Field(None, alias="_id", description="Internal task ID")
    uuid: str = Field(
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        description="Task UUID",
    )
    status: int = Field(ge=0, le=100, description="Task completion rate (%)")
    remaining: int = Field(ge=0, description="Number of seconds until task completion")
    times: TaskTimesDto = Field(description="Task timing information")
    public: TaskPublicDto = Field(description="Public task information")
    usersTags: List[str] = Field(default=[], description="User defined tags")
    tags: List[str] = Field(default=[], description="System tags")
    scores: TaskScoresDto = Field(description="Task scores")
    actions: TaskActionsDto = Field(description="Task actions")
    threats: List[str] = Field(default=[], description="Detected threats")


class TaskStatusUpdateDto(BaseModel):
    """Task status update model."""

    task: TaskStatusDto = Field(description="Task status information")
    completed: bool = Field(description="Task completion status")
    error: Literal[False] = Field(False, description="Error status")
