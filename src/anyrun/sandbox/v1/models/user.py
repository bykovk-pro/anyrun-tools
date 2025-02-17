"""User models for Sandbox API v1."""

from datetime import datetime
from typing import Any, Dict, List, Optional

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

    id: str = Field(alias="_id", description="Preset ID")
    name: str = Field(description="Preset name")
    user_id: str = Field(alias="userId", description="User ID")
    user_plan_name: str = Field(alias="userPlanName", description="User plan name")
    create_time: datetime = Field(alias="createTime", description="Creation time")

    # Environment settings
    os: str = Field(description="Operating system")
    version: str = Field(description="OS version")
    bitness: int = Field(description="OS bitness")
    type: str = Field(description="Environment type")
    browser: str = Field(description="Browser")
    locale: str = Field(description="Locale")
    location: str = Field(description="Start location")

    # Network settings
    net_connected: bool = Field(alias="netConnected", description="Network connected")
    network: str = Field(description="Network type")
    fakenet: bool = Field(description="FakeNet enabled")
    mitm: bool = Field(description="MITM enabled")
    netviator: bool = Field(description="Netviator enabled")
    vpn: bool = Field(description="VPN enabled")
    open_vpn: str = Field(alias="openVPN", description="OpenVPN configuration")
    tor_geo: str = Field(alias="torGeo", description="TOR geography")
    residential_proxy: bool = Field(
        alias="residentialProxy", description="Residential proxy enabled"
    )
    residential_proxy_geo: str = Field(
        alias="residentialProxyGeo", description="Residential proxy geography"
    )

    # Additional settings
    timeout: int = Field(description="Timeout in seconds")
    privacy: str = Field(description="Privacy type")
    hide_source: bool = Field(alias="hide_source", description="Hide source")
    extension: bool = Field(description="Extension enabled")
    autoclicker: bool = Field(description="Autoclicker enabled")
    el: bool = Field(description="Elevation prompt")
    no_controls: bool = Field(alias="noControls", description="No controls")
    expiration_time: str = Field(alias="expirationTime", description="Expiration time")
    expiration_time_selected: bool = Field(
        alias="expirationTimeSelected", description="Expiration time selected"
    )


class UserPresetsResponse(BaseModel):
    """User presets response."""

    error: bool = Field(description="Error flag")
    data: List[UserPreset] = Field(description="List of user presets")

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Optional[Any] = None,
    ) -> "UserPresetsResponse":
        """Validate and create model from raw data.

        Args:
            obj: Raw data from API
            strict: Whether to enforce strict validation
            from_attributes: Whether to extract data from object attributes
            context: Optional context for validation

        Returns:
            UserPresetsResponse: Validated model
        """
        if isinstance(obj, list):
            # API returns list of presets directly
            return cls(error=False, data=[UserPreset.model_validate(item) for item in obj])
        elif isinstance(obj, dict):
            # API returns wrapped response
            return cls(
                error=obj["error"],
                data=[UserPreset.model_validate(item) for item in obj["data"]],
            )
        else:
            raise ValueError(f"Invalid response format: {type(obj)}")
