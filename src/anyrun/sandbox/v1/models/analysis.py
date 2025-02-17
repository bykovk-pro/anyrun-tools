"""Analysis models for Sandbox API v1."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    ValidationInfo,
    field_validator,
    model_validator,
)

from .task_status_update import TaskStatusDto


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


class GeoLocation(str, Enum):
    """Geographic location for TOR and residential proxy."""
    FASTEST = "fastest"
    AU = "AU"  # Australia
    BR = "BR"  # Brazil
    CH = "CH"  # Switzerland
    DE = "DE"  # Germany
    FR = "FR"  # France
    GB = "GB"  # United Kingdom
    IT = "IT"  # Italy
    KR = "KR"  # South Korea
    RU = "RU"  # Russia
    US = "US"  # United States


class AnalysisRequest(BaseModel):
    """Analysis request parameters."""

    # Object parameters
    obj_type: ObjectType = Field(default=ObjectType.FILE, description="Type of new task")
    file: Optional[bytes] = Field(None, description="Required when obj_type=file")
    obj_url: Optional[HttpUrl] = Field(None, description="Required when obj_type=url or obj_type=download")
    task_rerun_uuid: Optional[str] = Field(None, description="Required when obj_type=rerun")

    # Environment parameters
    env_os: Optional[OSType] = Field(None, description="Operation System")
    env_version: Optional[str] = Field(None, description="OS version")
    env_bitness: Optional[BitnessType] = Field(None, description="Bitness of Operation System")
    env_type: Optional[EnvType] = Field(None, description="Environment type")
    env_locale: Optional[str] = Field(None, description="Operation system's language")

    # Object execution parameters
    obj_ext_cmd: Optional[str] = Field(None, min_length=0, max_length=256, description="Optional command line (Windows only)")
    obj_ext_browser: Optional[Browser] = Field(None, description="Browser type")
    obj_ext_useragent: Optional[str] = Field(None, min_length=0, max_length=256, description="User agent for download type")
    obj_ext_elevateprompt: Optional[bool] = Field(None, description="Windows only")
    obj_force_elevation: Optional[bool] = Field(None, description="Windows only")
    auto_confirm_uac: Optional[bool] = Field(None, description="Windows only")
    run_as_root: Optional[bool] = Field(None, description="Linux only")
    obj_ext_extension: Optional[bool] = Field(None, description="Extension enabled")
    obj_ext_startfolder: Optional[StartFolder] = Field(None, description="Start object folder")

    # Network options
    opt_network_connect: Optional[bool] = Field(None, description="Network connection state")
    opt_network_fakenet: Optional[bool] = Field(None, description="FakeNet feature status")
    opt_network_tor: Optional[bool] = Field(None, description="TOR using")
    opt_network_geo: Optional[GeoLocation] = Field(None, description="Geographic location for TOR traffic")
    opt_network_mitm: Optional[bool] = Field(None, description="HTTPS MITM proxy option")
    opt_network_residential_proxy: Optional[bool] = Field(None, description="Residential proxy for network traffic")
    opt_network_residential_proxy_geo: Optional[GeoLocation] = Field(None, description="Geographic location for residential proxy")

    # Timeout options
    opt_timeout: Optional[int] = Field(None, ge=10, le=1200, description="Execution time in seconds (10-1200)")

    # Privacy options
    opt_privacy_type: Optional[PrivacyType] = Field(None, description="Privacy settings")
    opt_privacy_hidesource: Optional[bool] = Field(None, description="Option for hiding source URL")

    # Advanced options
    opt_chatgpt: Optional[bool] = Field(None, description="ChatGPT option")
    opt_automated_interactivity: Optional[bool] = Field(None, description="Automated Interactivity (ML) option")

    # Tags
    user_tags: Optional[str] = Field(None, description="Pattern: a-z, A-Z, 0-9, hyphen (-), comma (,). Max length per tag: 16 chars, max tags: 8")

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


class TaskStatusUpdateDto(BaseModel):
    """Task status update model."""
    task: TaskStatusDto = Field(description="Task status information")
    completed: bool = Field(description="Task completion status")
    error: bool = Field(description="Error status")


class AnalysisData(BaseModel):
    """Analysis data model."""
    taskid: Optional[str] = Field(None, description="Task ID (used in create response)")
    task_id: Optional[str] = Field(None, description="Task ID (used in status response)")
    status: Optional[str] = Field(None, description="Task status")
    completed: Optional[bool] = Field(None, description="Task completion status")
    verdict: Optional[Dict[str, Any]] = Field(None, description="Analysis verdict")
    task: Optional[TaskStatusDto] = Field(None, description="Task status information")

    @model_validator(mode="after")
    def convert_taskid(self) -> "AnalysisData":
        """Convert taskid to task_id if needed."""
        if self.taskid and not self.task_id:
            self.task_id = self.taskid
            self.taskid = None
        return self

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Override model_dump to handle special fields.

        Args:
            **kwargs: Additional arguments passed to model_dump

        Returns:
            Dict[str, Any]: Serialized model data
        """
        data = super().model_dump(**kwargs)
        # Convert data to mutable dict if it's not
        if not isinstance(data, dict):
            data = dict(data)
        return data


class AnalysisResponse(BaseModel):
    """Analysis response."""
    error: bool = Field(description="Error flag")
    data: AnalysisData = Field(description="Response data")
    message: Optional[str] = Field(None, description="Error message")

    @model_validator(mode="after")
    def validate_data(self) -> "AnalysisResponse":
        """Validate response data."""
        data_dict = self.data.model_dump()
        if not self.error and "taskid" in data_dict and data_dict["taskid"]:
            self.data.task_id = data_dict["taskid"]
            self.data.taskid = None
        return self


class AnalysisListRequest(BaseModel):
    """Analysis list request parameters."""

    team: bool = Field(
        default=False, description="Get team history instead of personal"
    )
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=25, ge=1, le=100, description="Number of items per page")


class AnalysisListItem(BaseModel):
    """Analysis list item model."""
    uuid: str = Field(description="Task UUID")
    verdict: Optional[str] = Field(None, description="Analysis verdict")
    name: Optional[str] = Field(None, description="Name of the main object")
    related: Optional[HttpUrl] = Field(None, description="URL of the main analysis report")
    pcap: Optional[HttpUrl] = Field(None, description="URL for downloading PCAP file")
    file: Optional[HttpUrl] = Field(None, description="URL for downloading the main object")
    json: Optional[HttpUrl] = Field(None, description="URL of the JSON report")
    misp: Optional[HttpUrl] = Field(None, description="URL of the MISP report")
    date: Optional[datetime] = Field(None, description="Analysis creation timestamp")
    tags: List[str] = Field(default=[], description="Analysis tags")
    hashes: Optional[Dict[str, str]] = Field(None, description="Object hashes")


class AnalysisListData(BaseModel):
    """Analysis list data model."""
    tasks: List[AnalysisListItem] = Field(description="List of analysis items")


class AnalysisListResponse(BaseModel):
    """Analysis list response."""
    error: bool = Field(description="Error flag")
    data: AnalysisListData = Field(description="Response data")
    message: Optional[str] = Field(None, description="Error message")

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Override model_dump to handle HttpUrl and datetime serialization.

        Args:
            **kwargs: Additional arguments passed to model_dump

        Returns:
            Dict[str, Any]: Serialized model data
        """
        data = super().model_dump(**kwargs)
        if "data" in data and "tasks" in data["data"]:
            for item in data["data"]["tasks"]:
                if "related" in item and item["related"]:
                    item["related"] = str(item["related"])
                if "pcap" in item and item["pcap"]:
                    item["pcap"] = str(item["pcap"])
                if "file" in item and item["file"]:
                    item["file"] = str(item["file"])
                if "json" in item and item["json"]:
                    item["json"] = str(item["json"])
                if "misp" in item and item["misp"]:
                    item["misp"] = str(item["misp"])
                if "date" in item and item["date"]:
                    item["date"] = item["date"].isoformat()
        return data


class AddTimeResponse(BaseModel):
    """Response model for add time request."""

    error: bool = Field(description="Error flag")
    message: str = Field(description="Response message")


class StopAnalysisResponse(BaseModel):
    """Stop analysis response."""

    error: bool = Field(description="Error flag")
    message: str = Field(description="Response message")


class DeleteAnalysisResponse(BaseModel):
    """Delete analysis response."""

    error: bool = Field(description="Error flag")
    message: str = Field(description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Optional response data")


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

    # Analysis information
    uuid: str = Field(description="Analysis UUID")
    permanentUrl: HttpUrl = Field(description="URL of the main analysis report")
    duration: int = Field(description="Duration of the analysis in seconds")
    creation: int = Field(description="Timestamp of the analysis creation")
    creationText: str = Field(description="Human-readable timestamp of the analysis creation")
    stopExec: Optional[int] = Field(None, description="Timestamp of the analysis completion")
    stopExecText: Optional[str] = Field(None, description="Human-readable timestamp of the analysis completion")

    # Reports
    reports: Dict[str, HttpUrl] = Field(description="URLs of various report formats")
    tags: List[str] = Field(default=[], description="Analysis tags")

    # Sandbox information
    sandbox: Dict[str, Any] = Field(description="Sandbox information")
    options: Dict[str, Any] = Field(description="Analysis options")
    scores: Dict[str, Any] = Field(description="Analysis scores")

    # Content
    content: Dict[str, Any] = Field(description="Analysis content")

    # Environment
    environments: Dict[str, Any] = Field(description="Environment information")
    counters: Dict[str, Any] = Field(description="Analysis counters")

    # Results
    processes: List[Dict[str, Any]] = Field(default=[], description="Process information")
    network: Dict[str, Any] = Field(description="Network activity")
    modified: Dict[str, Any] = Field(description="Modified files and registry")
    incidents: List[Dict[str, Any]] = Field(default=[], description="Detected incidents")
    mitre: List[Dict[str, Any]] = Field(default=[], description="MITRE ATT&CK information")
    malconf: List[Dict[str, Any]] = Field(default=[], description="Malware configuration")
    debugStrings: List[Dict[str, Any]] = Field(default=[], description="Debug strings")

    # Status
    status: str = Field(description="Task completion status")

    # Basic information
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
    opt_network_geo: Optional[str] = None
    opt_network_mitm: bool = Field(description="HTTPS MITM proxy option")
    opt_network_residential_proxy: Optional[bool] = None
    opt_network_residential_proxy_geo: Optional[str] = None
    opt_timeout: Optional[int] = None
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


class FileAnalysisRequest(AnalysisRequest):
    """File analysis request parameters."""
    obj_type: ObjectType = Field(default=ObjectType.FILE, frozen=True, description="Type of new task")
    file: bytes = Field(description="File content")


class URLAnalysisRequest(AnalysisRequest):
    """URL analysis request parameters."""
    obj_type: ObjectType = Field(default=ObjectType.URL, frozen=True, description="Type of new task")
    obj_url: HttpUrl = Field(description="Target URL")


class DownloadAnalysisRequest(AnalysisRequest):
    """Download analysis request parameters."""
    obj_type: ObjectType = Field(default=ObjectType.DOWNLOAD, frozen=True, description="Type of new task")
    obj_url: HttpUrl = Field(description="URL to download and analyze")


class RerunAnalysisRequest(AnalysisRequest):
    """Rerun analysis request parameters."""
    obj_type: ObjectType = Field(default=ObjectType.RERUN, frozen=True, description="Type of new task")
    task_rerun_uuid: str = Field(description="Task UUID to rerun")
