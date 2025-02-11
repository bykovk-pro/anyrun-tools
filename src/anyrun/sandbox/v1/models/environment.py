"""Environment models for Sandbox API v1."""

from pydantic import BaseModel


class EnvironmentResponse(BaseModel):
    """Environment information response."""

    error: bool
    data: dict
