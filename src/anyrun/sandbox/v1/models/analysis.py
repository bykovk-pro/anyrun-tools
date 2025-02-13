"""Analysis models for Sandbox API v1."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    ValidationInfo,
    field_validator,
    model_validator,
)


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
    env_os: OSType = Field(default=OSType.WINDOWS, description="Operation System")
    env_version: Optional[str] = Field(None, description="OS version")
    env_bitness: BitnessType = Field(
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
    def validate_required_fields(self) -> "AnalysisRequest":
        """Validate required fields based on obj_type."""
        if self.obj_type == ObjectType.FILE and not self.file:
            raise ValueError("file is required when obj_type is file")
        if self.obj_type in (ObjectType.URL, ObjectType.DOWNLOAD) and not self.obj_url:
            raise ValueError("obj_url is required when obj_type is url or download")
        if self.obj_type == ObjectType.RERUN and not self.task_rerun_uuid:
            raise ValueError("task_rerun_uuid is required when obj_type is rerun")
        return self

    @field_validator("env_version")
    @classmethod
    def validate_os_version(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        """Validate OS version based on env_os."""
        if not v:
            return v
        env_os = info.data.get("env_os")
        if env_os == OSType.WINDOWS:
            if v not in [ver.value for ver in WindowsVersion]:
                raise ValueError("Invalid Windows version")
        elif env_os == OSType.LINUX:
            if v not in [ver.value for ver in LinuxVersion]:
                raise ValueError("Invalid Linux version")
        return v

    @field_validator("env_type")
    @classmethod
    def validate_env_type(
        cls, v: Optional[EnvType], info: ValidationInfo
    ) -> Optional[EnvType]:
        """Validate environment type based on OS."""
        if not v:
            return v
        env_os = info.data.get("env_os")
        if env_os == OSType.LINUX and v != EnvType.OFFICE:
            raise ValueError('Only "office" environment type is allowed for Linux')
        return v

    @field_validator("env_bitness")
    @classmethod
    def validate_bitness(cls, v: BitnessType, info: ValidationInfo) -> BitnessType:
        """Validate bitness based on OS and version."""
        env_os = info.data.get("env_os")
        env_version = info.data.get("env_version")
        if env_os == OSType.LINUX and v != BitnessType.X64:
            raise ValueError("Only 64-bit is supported for Linux")
        if env_os == OSType.WINDOWS:
            if env_version == WindowsVersion.WIN11.value and v != BitnessType.X64:
                raise ValueError("Only 64-bit is supported for Windows 11")
        return v

    @field_validator("obj_ext_browser")
    @classmethod
    def validate_browser(
        cls, v: Optional[Browser], info: ValidationInfo
    ) -> Optional[Browser]:
        """Validate browser based on OS."""
        if not v:
            return v
        env_os = info.data.get("env_os")
        if env_os == OSType.LINUX and v not in (Browser.CHROME, Browser.FIREFOX):
            raise ValueError("Only Chrome and Firefox are supported for Linux")
        return v

    @field_validator("obj_ext_startfolder")
    @classmethod
    def validate_startfolder(
        cls, v: Optional[StartFolder], info: ValidationInfo
    ) -> Optional[StartFolder]:
        """Validate start folder based on OS."""
        if not v:
            return v
        env_os = info.data.get("env_os")
        if env_os == OSType.LINUX and v in (
            StartFolder.APPDATA,
            StartFolder.ROOT,
            StartFolder.WINDOWS,
        ):
            raise ValueError(f"Start folder {v} is not supported for Linux")
        return v


class AnalysisResponse(BaseModel):
    """Analysis response."""

    error: bool
    data: dict


class AnalysisListRequest(BaseModel):
    """Analysis list request parameters."""

    team: bool = Field(
        default=False, description="Get team history instead of personal"
    )
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=25, ge=1, le=100, description="Number of items per page")


class AnalysisListResponse(BaseModel):
    """Analysis list response."""

    error: bool
    data: dict


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


class AnalysisStatus(str, Enum):
    """Analysis status."""

    QUEUED = "queued"
    STARTING = "starting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisResult(BaseModel):
    """Analysis result model."""

    # Basic information
    uuid: str = Field(description="Analysis UUID")
    status: AnalysisStatus = Field(description="Analysis status")
    created_at: datetime = Field(description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error: Optional[str] = Field(None, description="Error message")

    # Object information
    obj_type: ObjectType = Field(description="Object type")
    obj_url: Optional[HttpUrl] = Field(None, description="Object URL")
    obj_hash: Optional[str] = Field(None, description="Object hash")
    obj_filename: Optional[str] = Field(None, description="Object filename")
    obj_size: Optional[int] = Field(None, description="Object size in bytes")
    obj_mime: Optional[str] = Field(None, description="Object MIME type")

    # Environment information
    env_os: OSType = Field(description="Operating system type")
    env_bitness: BitnessType = Field(description="Operating system bitness")
    env_version: str = Field(description="Operating system version")
    env_type: EnvType = Field(description="Environment type")
    env_browser: Optional[Browser] = Field(None, description="Browser type")

    # Analysis options
    opt_network_connect: bool = Field(description="Network connection state")
    opt_network_fakenet: bool = Field(description="FakeNet feature status")
    opt_network_tor: bool = Field(description="TOR using")
    opt_network_mitm: bool = Field(description="HTTPS MITM proxy option")
    opt_privacy_type: PrivacyType = Field(description="Privacy settings")
    opt_privacy_hidesource: bool = Field(description="Option for hiding source URL")
    opt_chatgpt: Optional[bool] = None

    # Analysis results
    result_score: Optional[int] = Field(None, description="Analysis score")
    result_verdict: Optional[str] = Field(None, description="Analysis verdict")
    result_categories: Optional[List[str]] = Field(
        None, description="Analysis categories"
    )
    result_tags: Optional[List[str]] = Field(None, description="Analysis tags")
    result_mitre: Optional[List[str]] = Field(
        None, description="MITRE ATT&CK techniques"
    )
    result_iocs: Optional[Dict[str, Any]] = Field(None, description="Extracted IOCs")
    result_files: Optional[Dict[str, Any]] = Field(None, description="Generated files")
    result_screenshots: Optional[Dict[str, Any]] = Field(
        None, description="Screenshots"
    )
    result_pcap: Optional[Dict[str, Any]] = Field(None, description="Network traffic")
    result_report: Optional[Dict[str, Any]] = Field(None, description="Analysis report")
    result_summary: Optional[Dict[str, Any]] = Field(
        None, description="Analysis summary"
    )
    result_errors: Optional[List[str]] = Field(None, description="Analysis errors")

    # Additional information
    user_id: Optional[str] = Field(None, description="User ID")
    team_id: Optional[str] = Field(None, description="Team ID")
    share_url: Optional[HttpUrl] = Field(None, description="Share URL")
    report_url: Optional[HttpUrl] = Field(None, description="Report URL")
    download_url: Optional[HttpUrl] = Field(None, description="Download URL")
    pcap_url: Optional[HttpUrl] = Field(None, description="PCAP URL")
    screenshots_url: Optional[HttpUrl] = Field(None, description="Screenshots URL")
    files_url: Optional[HttpUrl] = Field(None, description="Files URL")
    report_pdf_url: Optional[HttpUrl] = Field(None, description="PDF report URL")
    report_json_url: Optional[HttpUrl] = Field(None, description="JSON report URL")
    report_html_url: Optional[HttpUrl] = Field(None, description="HTML report URL")
    report_xml_url: Optional[HttpUrl] = Field(None, description="XML report URL")
    report_txt_url: Optional[HttpUrl] = Field(None, description="TXT report URL")
    report_csv_url: Optional[HttpUrl] = Field(None, description="CSV report URL")
    report_md_url: Optional[HttpUrl] = Field(None, description="Markdown report URL")
    report_yaml_url: Optional[HttpUrl] = Field(None, description="YAML report URL")
    report_stix_url: Optional[HttpUrl] = Field(None, description="STIX report URL")
    report_misp_url: Optional[HttpUrl] = Field(None, description="MISP report URL")
    report_openioc_url: Optional[HttpUrl] = Field(
        None, description="OpenIOC report URL"
    )
    report_cybox_url: Optional[HttpUrl] = Field(None, description="CybOX report URL")
    report_maec_url: Optional[HttpUrl] = Field(None, description="MAEC report URL")
    report_cef_url: Optional[HttpUrl] = Field(None, description="CEF report URL")
    report_leef_url: Optional[HttpUrl] = Field(None, description="LEEF report URL")
