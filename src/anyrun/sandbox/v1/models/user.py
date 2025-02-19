"""User models for Sandbox API v1."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from .request_types import RequestGeoLocation, RequestNetworkType, RequestOSType, RequestPrivacyType
from .response_types import (
    ResponseGeoLocation,
    ResponseNetworkType,
    ResponseOSType,
    ResponsePrivacyType,
)


class UserInfoRequest(BaseModel):
    """User info request parameters."""

    team: bool = Field(default=False, description="Get team info instead of personal")


class UserLimitsDto(BaseModel):
    """User account limits."""

    web: Dict[str, int] = Field(description="Defines limits for interactive usage")
    api: Dict[str, int] = Field(description="Defines limits for API usage")
    parallels: Dict[str, int] = Field(description="Defines limits for parallel runs")


class UserInfoData(BaseModel):
    """User info data model."""

    limits: UserLimitsDto = Field(description="User account limits")


class UserInfoResponse(BaseModel):
    """User info response."""

    error: Literal[False] = Field(False, description="Error flag")
    data: UserInfoData = Field(description="Response data")


class UserPresetRequest(BaseModel):
    """User preset request model."""

    name: str = Field(min_length=1, max_length=64, description="Preset name")

    # Environment settings
    os: RequestOSType = Field(description="Operating system")
    version: str = Field(pattern="^(7|10|11|22\\.04\\.2)$", description="OS version")
    bitness: int = Field(ge=32, le=64, description="OS bitness")
    type: str = Field(pattern="^(clean|office|complete)$", description="Environment type")
    browser: str = Field(
        pattern="^(Google Chrome|Mozilla Firefox|Internet Explorer|Microsoft Edge)$",
        description="Browser",
    )
    locale: str = Field(description="Locale")
    location: str = Field(
        pattern="^(desktop|downloads|home|temp|appdata|root|windows)$",
        description="Start location",
    )

    # Network settings
    net_connected: bool = Field(alias="netConnected", description="Network connected")
    network: RequestNetworkType = Field(description="Network type")
    fakenet: bool = Field(description="FakeNet enabled")
    mitm: bool = Field(description="MITM enabled")
    netviator: bool = Field(description="Netviator enabled")
    vpn: bool = Field(description="VPN enabled")
    open_vpn: str = Field(alias="openVPN", description="OpenVPN configuration")
    tor_geo: RequestGeoLocation = Field(alias="torGeo", description="TOR geography")
    residential_proxy: bool = Field(
        alias="residentialProxy", description="Residential proxy enabled"
    )
    residential_proxy_geo: RequestGeoLocation = Field(
        alias="residentialProxyGeo", description="Residential proxy geography"
    )

    # Additional settings
    timeout: int = Field(ge=10, le=1200, description="Timeout in seconds")
    privacy: RequestPrivacyType = Field(description="Privacy type")
    hide_source: bool = Field(alias="hide_source", description="Hide source")
    extension: bool = Field(description="Extension enabled")
    autoclicker: bool = Field(description="Autoclicker enabled")
    el: bool = Field(description="Elevation prompt")
    no_controls: bool = Field(alias="noControls", description="No controls")


class UserPresetResponse(BaseModel):
    """User preset response model."""

    id: str = Field(alias="_id", description="Preset ID")
    name: str = Field(min_length=1, max_length=64, description="Preset name")
    user_id: str = Field(alias="userId", description="User ID")
    user_plan_name: str = Field(alias="userPlanName", description="User plan name")
    create_time: datetime = Field(alias="createTime", description="Creation time")

    # Environment settings
    os: ResponseOSType = Field(description="Operating system")
    version: str = Field(pattern="^(7|10|11|22\\.04\\.2)$", description="OS version")
    bitness: int = Field(ge=32, le=64, description="OS bitness")
    type: str = Field(pattern="^(clean|office|complete)$", description="Environment type")
    browser: str = Field(
        pattern="^(Google Chrome|Mozilla Firefox|Internet Explorer|Microsoft Edge)$",
        description="Browser",
    )
    locale: str = Field(description="Locale")
    location: str = Field(
        pattern="^(desktop|downloads|home|temp|appdata|root|windows)$",
        description="Start location",
    )

    # Network settings
    net_connected: bool = Field(alias="netConnected", description="Network connected")
    network: ResponseNetworkType = Field(description="Network type")
    fakenet: bool = Field(description="FakeNet enabled")
    mitm: bool = Field(description="MITM enabled")
    netviator: bool = Field(description="Netviator enabled")
    vpn: bool = Field(description="VPN enabled")
    open_vpn: str = Field(alias="openVPN", description="OpenVPN configuration")
    tor_geo: ResponseGeoLocation = Field(alias="torGeo", description="TOR geography")
    residential_proxy: bool = Field(
        alias="residentialProxy", description="Residential proxy enabled"
    )
    residential_proxy_geo: ResponseGeoLocation = Field(
        alias="residentialProxyGeo", description="Residential proxy geography"
    )

    # Additional settings
    timeout: int = Field(ge=10, le=1200, description="Timeout in seconds")
    privacy: ResponsePrivacyType = Field(description="Privacy type")
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

    error: Literal[False] = Field(False, description="Error flag")
    data: List[UserPresetResponse] = Field(description="List of user presets")

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
            return cls(
                error=False,
                data=[UserPresetResponse.model_validate(item) for item in obj],
            )
        elif isinstance(obj, dict):
            # API returns wrapped response
            return cls(
                error=obj["error"],
                data=[UserPresetResponse.model_validate(item) for item in obj["data"]],
            )
        else:
            raise ValueError(f"Invalid response format: {type(obj)}")
