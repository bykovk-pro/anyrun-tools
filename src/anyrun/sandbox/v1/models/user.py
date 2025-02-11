"""User models for Sandbox API v1."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator


class UserInfoRequest(BaseModel):
    """User info request parameters."""

    team: bool = Field(default=False, description="Get team info instead of personal")


class UserInfoResponse(BaseModel):
    """User info response."""

    error: bool = Field(description="Error flag")
    data: Dict[str, Any] = Field(description="Response data")


class UserPreset(BaseModel):
    """User preset model."""

    id: str = Field(description="Preset ID")
    name: str = Field(description="Preset name")
    settings: Dict[str, Any] = Field(description="Preset settings")


class UserPresetsResponse(BaseModel):
    """User presets response."""

    error: bool = Field(description="Error flag")
    data: List[Dict[str, Any]] = Field(description="List of user presets")

    @field_validator("data")
    @classmethod
    def validate_presets(cls, v: List[Any]) -> List[Dict[str, Any]]:
        """Validate presets data.

        Args:
            v: List of presets

        Returns:
            List[Dict[str, Any]]: Validated presets

        Raises:
            ValueError: If presets data is invalid
        """
        if not isinstance(v, list):
            raise ValueError("Presets data must be a list")

        for preset in v:
            if not isinstance(preset, dict):
                raise ValueError("Each preset must be a dictionary")
            if "id" not in preset:
                raise ValueError('Each preset must have an "id" field')
            if "name" not in preset:
                raise ValueError('Each preset must have a "name" field')
            if "settings" not in preset:
                raise ValueError('Each preset must have a "settings" field')

        return v

    @property
    def presets(self) -> List[UserPreset]:
        """Get presets as UserPreset objects.

        Returns:
            List[UserPreset]: List of user presets
        """
        return [UserPreset(**preset) for preset in self.data]
