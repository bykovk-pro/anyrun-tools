"""Schemas for Sandbox API data validation."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, model_validator


class ObjectType(str, Enum):
    """Analysis object type."""

    FILE = "file"
    URL = "url"
    DOWNLOAD = "download"
    RERUN = "rerun"


class OSType(str, Enum):
    """Operating system type."""

    WINDOWS = "windows"
    LINUX = "linux"


class BitnessType(str, Enum):
    """Operation System bitness type.

    For Linux: only 64
    For Win11: only 64
    For Win7/10: 32 or 64
    """

    X32 = "32"
    X64 = "64"


class WindowsVersion(str, Enum):
    """Windows version."""

    WIN7 = "7"
    WIN10 = "10"
    WIN11 = "11"


class LinuxVersion(str, Enum):
    """Linux version."""

    UBUNTU_22_04_2 = "22.04.2"


class EnvType(str, Enum):
    """Environment type.

    For Windows: clean, office, complete
    For Linux: only office
    """

    CLEAN = "clean"
    OFFICE = "office"
    COMPLETE = "complete"


class Browser(str, Enum):
    """Browser type.

    Default value for Windows: Microsoft Edge
    Allowed values for Windows: Google Chrome, Mozilla Firefox, Internet Explorer, Microsoft Edge
    Default value for Linux: Google Chrome
    Allowed values for Linux: Mozilla Firefox, Google Chrome
    """

    CHROME = "Google Chrome"
    FIREFOX = "Mozilla Firefox"
    IE = "Internet Explorer"
    EDGE = "Microsoft Edge"


class PrivacyType(str, Enum):
    """Privacy type."""

    PUBLIC = "public"
    BYLINK = "bylink"
    OWNER = "owner"
    BYTEAM = "byteam"


class StartFolder(str, Enum):
    """Start folder.

    Linux: desktop, downloads, home, temp
    Windows: appdata, desktop, downloads, home, root, temp, windows
    """

    DESKTOP = "desktop"
    DOWNLOADS = "downloads"
    HOME = "home"
    TEMP = "temp"
    APPDATA = "appdata"  # Windows only
    ROOT = "root"  # Windows only
    WINDOWS = "windows"  # Windows only


class AnalysisRequest(BaseModel):
    """Analysis request parameters."""

    # Object parameters
    obj_type: ObjectType = Field(
        default=ObjectType.FILE, description="Type of new task"
    )
    file: Optional[bytes] = Field(None, description="Required when obj_type=file")
    obj_url: Optional[HttpUrl] = Field(
        None, description="Required when obj_type=url or obj_type=download"
    )
    task_rerun_uuid: Optional[str] = Field(
        None, description="Required when obj_type=rerun"
    )

    # Environment parameters
    env_os: Optional[OSType] = Field(
        default=OSType.WINDOWS, description="Operation System"
    )
    env_version: Optional[str] = Field(None, description="OS version")
    env_bitness: Optional[BitnessType] = Field(
        default=BitnessType.X64, description="Bitness of Operation System"
    )
    env_type: Optional[EnvType] = None
    env_locale: Optional[str] = Field(None, description="Operation system's language")

    # Object execution parameters
    obj_ext_cmd: Optional[str] = Field(
        None,
        min_length=2,
        max_length=256,
        description="Optional command line (Windows only)",
    )
    obj_ext_browser: Optional[Browser] = None
    obj_ext_useragent: Optional[str] = Field(
        None, min_length=2, max_length=256, description="User agent for download type"
    )
    obj_ext_elevateprompt: Optional[bool] = Field(None, description="Windows only")
    obj_force_elevation: Optional[bool] = Field(None, description="Windows only")
    auto_confirm_uac: Optional[bool] = Field(default=True, description="Windows only")
    run_as_root: Optional[bool] = Field(default=False, description="Linux only")
    obj_ext_extension: Optional[bool] = None
    obj_ext_startfolder: Optional[StartFolder] = Field(
        default=StartFolder.TEMP, description="Start object folder"
    )

    # Network options
    opt_network_connect: Optional[bool] = Field(
        default=True, description="Network connection state"
    )
    opt_network_fakenet: Optional[bool] = Field(
        default=False, description="FakeNet feature status"
    )
    opt_network_tor: Optional[bool] = Field(default=False, description="TOR using")
    opt_network_mitm: Optional[bool] = Field(
        default=False, description="HTTPS MITM proxy option"
    )

    # Privacy options
    opt_privacy_type: Optional[PrivacyType] = Field(
        default=PrivacyType.BYLINK, description="Privacy settings"
    )
    opt_privacy_hidesource: Optional[bool] = Field(
        default=False, description="Option for hiding source URL"
    )

    # Advanced options
    opt_chatgpt: Optional[bool] = None
    opt_automated_interactivity: Optional[bool] = Field(
        default=True, description="Automated Interactivity (ML) option"
    )

    # Tags
    user_tags: Optional[str] = Field(
        None,
        description=(
            "Pattern: a-z, A-Z, 0-9, hyphen (-), comma (,). "
            "Max length per tag: 16 chars, max tags: 8"
        ),
    )

    @model_validator(mode="after")
    def validate_file_presence(self) -> "AnalysisRequest":
        """Validate that file is present when obj_type is FILE."""
        if self.obj_type == ObjectType.FILE and not self.file:
            raise ValueError("file is required when obj_type is file")
        if self.obj_type == ObjectType.URL and not self.obj_url:
            raise ValueError("obj_url is required when obj_type is url")
        if self.obj_type == ObjectType.DOWNLOAD and not self.obj_url:
            raise ValueError("obj_url is required when obj_type is download")
        if self.obj_type == ObjectType.RERUN and not self.task_rerun_uuid:
            raise ValueError("task_rerun_uuid is required when obj_type is rerun")
        return self


class AnalysisData(BaseModel):
    """Analysis data model."""

    task_id: str
    status: str


class AnalysisResponse(BaseModel):
    """Analysis response."""

    error: bool
    data: AnalysisData


class AnalysisListRequest(BaseModel):
    """Analysis list request parameters."""

    team: bool = Field(
        default=False, description="Get team history instead of personal"
    )
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=25, ge=1, le=100, description="Number of items per page")


class AnalysisListItem(BaseModel):
    """Analysis list item model."""

    task_id: str
    status: str


class AnalysisListData(BaseModel):
    """Analysis list data model."""

    items: List[AnalysisListItem]
    total: int


class AnalysisListResponse(BaseModel):
    """Analysis list response."""

    error: bool
    data: AnalysisListData


class WindowsEnvironment(BaseModel):
    """Windows environment model."""

    versions: List[str]
    bitness: List[str]


class LinuxEnvironment(BaseModel):
    """Linux environment model."""

    versions: List[str]
    bitness: List[str]


class EnvironmentData(BaseModel):
    """Environment data model."""

    windows: WindowsEnvironment
    linux: LinuxEnvironment


class EnvironmentResponse(BaseModel):
    """Environment information response."""

    error: bool
    data: EnvironmentData


class AddTimeResponse(BaseModel):
    """Response model for add time request."""

    error: bool = Field(description="Error flag")
    message: str = Field(description="Response message")


class StopAnalysisResponse(BaseModel):
    """Stop analysis response."""

    error: bool
    data: dict


class DeleteAnalysisResponse(BaseModel):
    """Delete analysis response."""

    error: bool
    data: dict
