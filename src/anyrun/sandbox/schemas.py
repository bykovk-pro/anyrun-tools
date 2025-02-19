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
    """Analysis request model."""

    # Object options
    obj_type: ObjectType = Field(description="Object type")
    obj_url: Optional[HttpUrl] = Field(None, description="Object URL")
    obj_hash: Optional[str] = Field(None, description="Object hash")
    obj_content: Optional[str] = Field(None, description="Object content")
    obj_filename: Optional[str] = Field(None, description="Object filename")

    # Environment options
    env_os: OSType = Field(description="Operating system type")
    env_bitness: BitnessType = Field(description="Operating system bitness")
    env_version: Optional[str] = Field(None, description="Operating system version")
    env_type: EnvType = Field(description="Environment type")
    env_browser: Optional[Browser] = Field(None, description="Browser type")

    # Object extension options
    obj_ext_runasadmin: Optional[bool] = Field(None, description="Run as admin")
    obj_ext_runwithargs: Optional[str] = Field(None, description="Run with arguments")
    obj_ext_runwithfile: Optional[str] = Field(None, description="Run with file")
    obj_ext_runwithurl: Optional[HttpUrl] = Field(None, description="Run with URL")
    obj_ext_runwithcontent: Optional[str] = Field(None, description="Run with content")
    obj_ext_runwithfilename: Optional[str] = Field(
        None,
        description="Run with filename",
        min_length=2,
        max_length=256,
    )
    obj_ext_elevateprompt: Optional[bool] = Field(
        None,
        description="Windows only",
    )
    obj_force_elevation: Optional[bool] = Field(
        None,
        description="Windows only",
    )
    auto_confirm_uac: Optional[bool] = Field(
        default=True,
        description="Windows only",
    )
    run_as_root: Optional[bool] = Field(
        default=False,
        description="Linux only",
    )
    obj_ext_extension: Optional[bool] = None
    obj_ext_startfolder: Optional[StartFolder] = Field(
        default=StartFolder.TEMP, description="Start object folder"
    )

    # Network options
    opt_network_connect: Optional[bool] = Field(
        default=True, description="Network connection state"
    )
    opt_network_fakenet: Optional[bool] = Field(default=False, description="FakeNet feature status")
    opt_network_tor: Optional[bool] = Field(default=False, description="TOR using")
    opt_network_mitm: Optional[bool] = Field(default=False, description="HTTPS MITM proxy option")

    # Privacy options
    opt_privacy_type: Optional[PrivacyType] = Field(
        default=PrivacyType.BYLINK, description="Privacy settings"
    )
    opt_privacy_hidesource: Optional[bool] = Field(
        default=False, description="Option for hiding source URL"
    )

    # Advanced options
    opt_chatgpt: Optional[bool] = None

    @model_validator(mode="after")  # type: ignore[misc]
    def validate_request(self) -> "AnalysisRequest":
        """Validate request.

        Returns:
            AnalysisRequest: Validated request

        Raises:
            ValueError: If request is invalid
        """
        # Validate object type
        if self.obj_type == ObjectType.FILE:
            if not self.obj_content:
                raise ValueError("Object content is required for file analysis")
            if not self.obj_filename:
                raise ValueError("Object filename is required for file analysis")
        elif self.obj_type == ObjectType.URL:
            if not self.obj_url:
                raise ValueError("Object URL is required for URL analysis")
        elif self.obj_type == ObjectType.DOWNLOAD:
            if not self.obj_url:
                raise ValueError("Object URL is required for download analysis")
        elif self.obj_type == ObjectType.RERUN:
            if not self.obj_hash:
                raise ValueError("Object hash is required for rerun analysis")

        # Validate environment
        if self.env_os == OSType.WINDOWS:
            if self.env_version not in WindowsVersion._value2member_map_:
                raise ValueError(
                    "Invalid Windows version. Supported: "
                    f"{list(WindowsVersion._value2member_map_.keys())}"
                )
            if self.env_version == WindowsVersion.WIN11 and self.env_bitness != BitnessType.X64:
                raise ValueError("Windows 11 supports only 64-bit")
            if self.env_type == EnvType.OFFICE and self.env_version == WindowsVersion.WIN11:
                raise ValueError("Windows 11 does not support office environment")
            if self.run_as_root:
                raise ValueError("Run as root is not supported for Windows")
        elif self.env_os == OSType.LINUX:
            if self.env_version not in LinuxVersion._value2member_map_:
                raise ValueError(
                    "Invalid Linux version. Supported: "
                    f"{list(LinuxVersion._value2member_map_.keys())}"
                )
            if self.env_bitness != BitnessType.X64:
                raise ValueError("Linux supports only 64-bit")
            if self.env_type != EnvType.OFFICE:
                raise ValueError("Linux supports only office environment")
            if self.obj_ext_elevateprompt or self.obj_force_elevation or self.auto_confirm_uac:
                raise ValueError("UAC options are not supported for Linux")

        # Validate browser
        if self.env_browser:
            if self.env_os == OSType.WINDOWS:
                if self.env_browser not in [
                    Browser.CHROME,
                    Browser.FIREFOX,
                    Browser.IE,
                    Browser.EDGE,
                ]:
                    raise ValueError(
                        "Invalid browser for Windows. Supported: "
                        "Google Chrome, Mozilla Firefox, Internet Explorer, Microsoft Edge"
                    )
            elif self.env_os == OSType.LINUX:
                if self.env_browser not in [Browser.CHROME, Browser.FIREFOX]:
                    raise ValueError(
                        "Invalid browser for Linux. Supported: " "Google Chrome, Mozilla Firefox"
                    )

        # Validate start folder
        if self.obj_ext_startfolder:
            if self.env_os == OSType.WINDOWS:
                if self.obj_ext_startfolder not in [
                    StartFolder.APPDATA,
                    StartFolder.DESKTOP,
                    StartFolder.DOWNLOADS,
                    StartFolder.HOME,
                    StartFolder.ROOT,
                    StartFolder.TEMP,
                    StartFolder.WINDOWS,
                ]:
                    raise ValueError(
                        "Invalid start folder for Windows. Supported: "
                        "appdata, desktop, downloads, home, root, temp, windows"
                    )
            elif self.env_os == OSType.LINUX:
                if self.obj_ext_startfolder not in [
                    StartFolder.DESKTOP,
                    StartFolder.DOWNLOADS,
                    StartFolder.HOME,
                    StartFolder.TEMP,
                ]:
                    raise ValueError(
                        "Invalid start folder for Linux. Supported: desktop, downloads, home, temp"
                    )

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

    team: bool = Field(default=False, description="Get team history instead of personal")
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
