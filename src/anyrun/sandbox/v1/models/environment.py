"""Environment models for Sandbox API v1."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AppDto(BaseModel):
    """Application information."""

    name: str = Field(description="Application name")
    version: str = Field(description="Application version")


class SoftwareDto(BaseModel):
    """Software information."""

    ie: Dict[str, Any] = Field(default={}, description="Internet Explorer information")
    upps: List[Any] = Field(default=[], description="Updates information")
    apps: List[AppDto] = Field(default=[], description="Installed applications")


class EnvironmentDto(BaseModel):
    """Environment information."""

    os: str = Field(description="Operating system type")
    software: SoftwareDto = Field(description="Installed software")
    bitness: int = Field(description="Environment bitness")
    type: Optional[str] = Field(None, description="Environment type")
    variant: Optional[str] = Field(None, description="Environment variant")
    version: Optional[str] = Field(None, description="Environment version")


class EnvironmentDataDto(BaseModel):
    """Environment data model."""

    environments: List[EnvironmentDto] = Field(description="List of available environments")


class EnvironmentResponse(BaseModel):
    """Environment information response."""

    error: Literal[False] = Field(False, description="Error flag")
    data: EnvironmentDataDto = Field(description="Response data")
