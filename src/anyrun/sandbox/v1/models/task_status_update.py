"""Task status update models for Sandbox API v1."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TaskScoresDto(BaseModel):
    """Task scores model."""
    specs: Dict[str, bool] = Field(description="Task specifications")
    verdict: Dict[str, Any] = Field(description="Task verdict")


class TaskPublicDto(BaseModel):
    """Task public information model."""
    maxAddedTimeReached: bool = Field(description="Maximum allowed task runtime reached")
    objects: Dict[str, Any] = Field(description="Task objects information")
    options: Dict[str, Any] = Field(description="Task options")
    environment: Dict[str, Any] = Field(description="Task environment information")


class TaskStatusDto(BaseModel):
    """Task status model."""
    id: Optional[str] = Field(None, alias="_id", description="Internal task ID")
    uuid: str = Field(description="Task UUID")
    status: int = Field(description="Task completion rate (%)")
    remaining: int = Field(description="Number of seconds until task completion")
    times: Dict[str, Any] = Field(description="Task timing information")
    public: TaskPublicDto = Field(description="Public task information")
    usersTags: List[str] = Field(default=[], description="User defined tags")
    tags: List[str] = Field(default=[], description="System tags")
    scores: TaskScoresDto = Field(description="Task scores")
    actions: Dict[str, Any] = Field(description="Task actions")
    threats: List[str] = Field(default=[], description="Detected threats")


class TaskStatusUpdateDto(BaseModel):
    """Task status update model."""
    task: TaskStatusDto = Field(description="Task status information")
    completed: bool = Field(description="Task completion status")
    error: bool = Field(description="Error status") 