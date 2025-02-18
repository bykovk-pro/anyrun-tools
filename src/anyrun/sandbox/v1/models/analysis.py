"""Analysis models for Sandbox API v1."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator

from .common import HashesApiDto, PrivacyType, ThreatLevelText
from .task_status_update import TaskStatusDto


# Base models
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


class TaskOptionsDto(BaseModel):
    """Task options model."""

    private: PrivacyType = Field(description="Privacy level")
    whitelist: List[str] = Field(default=[], description="Whitelisted items")
    mitm: bool = Field(description="MITM status")
    fakenet: bool = Field(description="FakeNet status")
    openVPN: str = Field(description="OpenVPN configuration")
    torGeo: Optional[str] = Field(None, description="TOR geography")
    netviator: bool = Field(description="Netviator status")
    netConnected: bool = Field(description="Network connection status")
    network: str = Field(description="Network type")
    logger: str = Field(description="Logger type")
    presentation: bool = Field(description="Presentation mode")
    teamwork: bool = Field(description="Team collaboration")
    reboots: bool = Field(description="System reboots")
    onlyimportant: bool = Field(description="Important events only")
    video: bool = Field(description="Video recording")
    locale: str = Field(description="System locale")
    residentialProxyGeo: Optional[str] = Field(None, description="Residential proxy geography")
    residentialProxy: bool = Field(description="Residential proxy status")
    autoclickerDebugMode: bool = Field(description="Autoclicker debug mode")
    autoclicker: bool = Field(description="Autoclicker status")
    chatGPT: bool = Field(description="ChatGPT integration")


class AnalysisRequest(BaseModel):
    """Analysis request parameters."""

    # Object parameters
    obj_type: ObjectType = Field(default=ObjectType.FILE, description="Type of new task")
    file: Optional[bytes] = Field(None, description="Required when obj_type=file")
    obj_url: Optional[str] = Field(
        None, description="Required when obj_type=url or obj_type=download"
    )
    task_rerun_uuid: Optional[str] = Field(None, description="Required when obj_type=rerun")

    # Environment parameters
    env_os: Optional[OSType] = Field(None, description="Operation System")
    env_version: Optional[str] = Field(None, description="OS version")
    env_bitness: Optional[BitnessType] = Field(None, description="Bitness of Operation System")
    env_type: Optional[EnvType] = Field(None, description="Environment type")
    env_locale: Optional[str] = Field(None, description="Operation system's language")

    # Object execution parameters
    obj_ext_cmd: Optional[str] = Field(
        None,
        min_length=0,
        max_length=256,
        description="Optional command line (Windows only)",
    )
    obj_ext_browser: Optional[Browser] = Field(None, description="Browser type")
    obj_ext_useragent: Optional[str] = Field(
        None,
        min_length=0,
        max_length=256,
        description="User agent for download type",
    )
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
    opt_network_geo: Optional[GeoLocation] = Field(
        None, description="Geographic location for TOR traffic"
    )
    opt_network_mitm: Optional[bool] = Field(None, description="HTTPS MITM proxy option")
    opt_network_residential_proxy: Optional[bool] = Field(
        None, description="Residential proxy for network traffic"
    )
    opt_network_residential_proxy_geo: Optional[GeoLocation] = Field(
        None, description="Geographic location for residential proxy"
    )

    # Timeout options
    opt_timeout: Optional[int] = Field(
        None, ge=10, le=1200, description="Execution time in seconds (10-1200)"
    )

    # Privacy options
    opt_privacy_type: Optional[PrivacyType] = Field(None, description="Privacy settings")
    opt_privacy_hidesource: Optional[bool] = Field(None, description="Option for hiding source URL")

    # Advanced options
    opt_chatgpt: Optional[bool] = Field(None, description="ChatGPT option")
    opt_automated_interactivity: Optional[bool] = Field(
        None, description="Automated Interactivity (ML) option"
    )

    # Tags
    user_tags: Optional[str] = Field(
        None,
        description=(
            "Pattern: a-z, A-Z, 0-9, hyphen (-), comma (,). "
            "Max length per tag: 16 chars, max tags: 8"
        ),
    )

    @model_validator(mode="after")  # type: ignore[misc]
    def validate_required_fields(self) -> "AnalysisRequest":
        """Validate required fields based on obj_type."""
        if self.obj_type == ObjectType.FILE and not self.file:
            raise ValueError("file is required when obj_type is file")
        if self.obj_type in (ObjectType.URL, ObjectType.DOWNLOAD) and not self.obj_url:
            raise ValueError("obj_url is required when obj_type is url or download")
        if self.obj_type == ObjectType.RERUN and not self.task_rerun_uuid:
            raise ValueError("task_rerun_uuid is required when obj_type is rerun")
        return self


class TaskUrlsDto(BaseModel):
    """Task URLs."""

    related: Optional[str] = Field(None, description="URL of the main analysis report")
    json_url: Optional[str] = Field(None, description="URL of the JSON report")
    misp: Optional[str] = Field(None, description="URL of the MISP report")
    pcap: Optional[str] = Field(None, description="URL for downloading PCAP file")
    file: Optional[str] = Field(None, description="URL for downloading the main object")


class BaseTaskHistoryDto(BaseModel):
    """Base class for task history items."""

    uuid: str = Field(
        pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        description="Task UUID",
    )
    verdict: ThreatLevelText = Field(description="Analysis verdict")
    date: datetime = Field(description="Analysis creation timestamp")
    tags: List[str] = Field(default=[], description="Analysis tags")
    hashes: HashesApiDto = Field(description="Object hashes")
    name: Optional[str] = Field(None, description="Name of the main object")
    related: Optional[str] = Field(None, description="URL of the main analysis report")
    json_url: Optional[str] = Field(None, description="URL of the JSON report")
    misp: Optional[str] = Field(None, description="URL of the MISP report")
    pcap: Optional[str] = Field(None, description="URL for downloading PCAP file")
    file: Optional[str] = Field(None, description="URL for downloading the main object")


class AnalysisListItem(BaseTaskHistoryDto):
    """Analysis list item model."""

    pass


class TaskHistoryDto(BaseTaskHistoryDto):
    """Task history item."""

    related: str = Field(description="URL of the main analysis report")
    json_url: str = Field(description="URL of the JSON report")
    misp: str = Field(description="URL of the MISP report")
    pcap: Optional[str] = Field(None, description="URL for downloading PCAP file")
    file: Optional[str] = Field(None, description="URL for downloading the main object")


class AnalysisListRequest(BaseModel):
    """Analysis list request parameters."""

    team: bool = Field(default=False, description="Get team history instead of personal")
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=25, ge=1, le=100, description="Number of items per page")


class TaskEnvironmentDto(BaseModel):
    """Task environment model."""

    OS: Dict[str, Any] = Field(description="Operating system information")
    software: List[Dict[str, Any]] = Field(default=[], description="Installed software")


class TaskObjectDto(BaseModel):
    """Task object model."""

    names: Dict[str, str] = Field(description="Object names")
    hashes: HashesApiDto = Field(description="Object hashes")
    urls: Optional[Dict[str, str]] = Field(None, description="Object URLs")


class TaskPublicDto(BaseModel):
    """Task public information model."""

    maxAddedTimeReached: bool = Field(
        default=False, description="Maximum allowed task runtime reached"
    )
    objects: TaskObjectDto = Field(description="Task objects information")
    options: TaskOptionsDto = Field(description="Task options")
    environment: TaskEnvironmentDto = Field(description="Task environment information")


class TaskTimesDto(BaseModel):
    """Task timing information."""

    created: datetime = Field(description="Task creation time")
    started: Optional[datetime] = Field(None, description="Task start time")
    completed: Optional[datetime] = Field(None, description="Task completion time")
    addedTime: Optional[datetime] = Field(None, description="Time when additional time was added")


class TaskActionsDto(BaseModel):
    """Task actions model."""

    addTime: bool = Field(default=False, description="Can add time")
    stop: bool = Field(default=False, description="Can stop task")
    delete: bool = Field(default=False, description="Can delete task")


class TaskStatusUpdateDto(BaseModel):
    """Task status update model."""

    task: TaskStatusDto = Field(description="Task status information")
    completed: bool = Field(default=False, description="Task completion status")
    error: Literal[False] = Field(default=False, description="Error status")


class AnalysisData(BaseModel):
    """Analysis data model."""

    taskid: Optional[str] = Field(None, description="Task ID (used in create response)")
    task_id: Optional[str] = Field(None, description="Task ID (used in status response)")
    status: Optional[str] = Field(None, description="Task status")
    completed: Optional[bool] = Field(None, description="Task completion status")
    verdict: Optional[Dict[str, Any]] = Field(None, description="Analysis verdict")
    task: Optional[TaskStatusDto] = Field(None, description="Task status information")

    @model_validator(mode="after")  # type: ignore[misc]
    def convert_taskid(self) -> "AnalysisData":
        """Convert taskid to task_id if needed."""
        if self.taskid and not self.task_id:
            self.task_id = self.taskid
            self.taskid = None
        return self


class AnalysisResponse(BaseModel):
    """Analysis response."""

    error: bool = Field(description="Error flag")
    data: AnalysisData = Field(description="Response data")
    message: Optional[str] = Field(None, description="Error message")

    @model_validator(mode="after")  # type: ignore[misc]
    def validate_data(self) -> "AnalysisResponse":
        """Validate response data."""
        if not self.error and self.data.taskid:
            self.data.task_id = self.data.taskid
            self.data.taskid = None
        return self


class AnalysisListData(BaseModel):
    """Analysis list data model."""

    tasks: List[AnalysisListItem] = Field(description="List of analysis items")


class AnalysisListResponse(BaseModel):
    """Analysis list response."""

    error: bool = Field(description="Error flag")
    data: AnalysisListData = Field(description="Response data")
    message: Optional[str] = Field(None, description="Error message")


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
    permanentUrl: str = Field(description="URL of the main analysis report")
    duration: int = Field(description="Duration of the analysis in seconds")
    creation: int = Field(description="Timestamp of the analysis creation")
    creationText: str = Field(description="Human-readable timestamp of the analysis creation")
    stopExec: Optional[int] = Field(None, description="Timestamp of the analysis completion")
    stopExecText: Optional[str] = Field(
        None, description="Human-readable timestamp of the analysis completion"
    )

    # Reports
    reports: Dict[str, str] = Field(description="URLs of various report formats")
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
    obj_url: Optional[str] = Field(None, description="Object URL")
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
    result_categories: Optional[List[str]] = Field(None, description="Analysis categories")
    result_tags: Optional[List[str]] = Field(None, description="Analysis tags")
    result_mitre: Optional[List[str]] = Field(None, description="MITRE ATT&CK techniques")
    result_iocs: Optional[Dict[str, Any]] = Field(None, description="Extracted IOCs")
    result_files: Optional[Dict[str, Any]] = Field(None, description="Generated files")
    result_screenshots: Optional[Dict[str, Any]] = Field(None, description="Screenshots")
    result_pcap: Optional[Dict[str, Any]] = Field(None, description="Network traffic")
    result_report: Optional[Dict[str, Any]] = Field(None, description="Analysis report")
    result_summary: Optional[Dict[str, Any]] = Field(None, description="Analysis summary")
    result_errors: Optional[List[str]] = Field(None, description="Analysis errors")

    # Additional information
    user_id: Optional[str] = Field(None, description="User ID")
    team_id: Optional[str] = Field(None, description="Team ID")


class FileAnalysisRequest(AnalysisRequest):
    """File analysis request parameters."""

    obj_type: Literal[ObjectType.FILE] = Field(
        default=ObjectType.FILE, frozen=True, description="Type of new task"
    )
    file: bytes = Field(description="File content")


class URLAnalysisRequest(AnalysisRequest):
    """URL analysis request parameters."""

    obj_type: Literal[ObjectType.URL] = Field(
        default=ObjectType.URL, frozen=True, description="Type of new task"
    )
    obj_url: str = Field(description="Target URL")


class DownloadAnalysisRequest(AnalysisRequest):
    """Download analysis request parameters."""

    obj_type: Literal[ObjectType.DOWNLOAD] = Field(
        default=ObjectType.DOWNLOAD, frozen=True, description="Type of new task"
    )
    obj_url: str = Field(description="URL to download and analyze")


class RerunAnalysisRequest(AnalysisRequest):
    """Rerun analysis request parameters."""

    obj_type: Literal[ObjectType.RERUN] = Field(
        default=ObjectType.RERUN, frozen=True, description="Type of new task"
    )
    task_rerun_uuid: str = Field(description="Task UUID to rerun")


# Base response models
class BaseResponseDto(BaseModel):
    """Base response model."""

    error: Literal[False] = Field(False, description="False indicates a successful request")


class ErrorResponseDto(BaseModel):
    """Error response model."""

    error: Literal[True] = Field(True, description="True indicates a failed request")
    message: str = Field(description="Provides information about the error")


class SuccessMessageDto(BaseResponseDto):
    """Success response with message."""

    message: Literal[
        "Add time in task successful",
        "Stop task successful",
        "Delete task successful",
    ] = Field(description="Contains response message")


# Success response models
class TaskIdResponse(BaseModel):
    """Response containing task ID."""

    taskid: str = Field(pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


class TaskHistoryResponse(BaseModel):
    """Response containing task history."""

    tasks: List[Dict[str, Any]]


class UserLimitsResponse(BaseModel):
    """Response containing user limits."""

    limits: Dict[str, Any]


class EnvironmentsResponse(BaseModel):
    """Response containing available environments."""

    environments: List[Dict[str, Any]]


class UserLimitsDto(BaseModel):
    """User account limits."""

    web: Dict[str, int] = Field(description="Defines limits for interactive usage")
    api: Dict[str, int] = Field(description="Defines limits for API usage")
    parallels: Dict[str, int] = Field(description="Defines limits for parallel runs")


class EnvironmentDto(BaseModel):
    """Environment information."""

    os: OSType
    version: Union[WindowsVersion, LinuxVersion]
    bitness: BitnessType
    build: Optional[int] = None
    variant: Optional[str] = None
    type: EnvType
    software: Dict[str, Any]


class SuccessResponseData(BaseModel):
    """Success response data model.

    According to API schema, exactly one of these fields must be present:
    - taskid: for task creation response
    - tasks: for task history response
    - limits: for user limits response
    - environments: for environment info response
    """

    taskid: Optional[str] = Field(
        None, pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    tasks: Optional[List[TaskHistoryDto]] = None
    limits: Optional[UserLimitsDto] = None
    environments: Optional[List[EnvironmentDto]] = None

    @model_validator(mode="after")  # type: ignore[misc]
    def validate_exactly_one_field(self) -> "SuccessResponseData":
        """Validate that exactly one field is present."""
        fields = {
            "taskid": self.taskid is not None,
            "tasks": self.tasks is not None,
            "limits": self.limits is not None,
            "environments": self.environments is not None,
        }
        present_fields = [field for field, present in fields.items() if present]
        if len(present_fields) != 1:
            raise ValueError(
                "Exactly one field must be present, "
                f"got {len(present_fields)}: {', '.join(present_fields)}"
            )
        return self


class SuccessResponseDto(BaseResponseDto):
    """Success response model."""

    data: SuccessResponseData = Field(description="Contains response data")


# Detailed data models
class TaskStatusMainObjectDto(BaseModel):
    """Main object information."""

    names: Dict[str, Any] = Field(description="Object names information")
    hashes: HashesApiDto = Field(description="Object hashes")


class TaskStatusVerdictDto(BaseModel):
    """Task verdict information."""

    threat_level: float = Field(description="Threat level of the analysis")
    text: ThreatLevelText = Field(description="Textual description of threat level")


class TaskStatusSpecsDto(BaseModel):
    """Task specifications."""

    autostart: bool = Field(description="Indicates if threat uses autostart feature")
    bad_module_certificate: bool = Field(description="Bad module certificate status")
    bad_process_certificate: bool = Field(description="Bad process certificate status")
    cpu_overrun: bool = Field(description="Indicates if overly high CPU usage was detected")
    crashed_apps: bool = Field(description="Indicates if any application crash was detected")
    crashed_task: bool = Field(description="Indicates if analysis task crash was detected")
    debug_output: bool = Field(description="Indicates if any debug data was extracted")
    executable_dropped: bool = Field(description="Indicates if threat uses dropped executables")
    exploitable: bool = Field(description="Indicates if any known exploit was detected")
    has_trace: bool = Field(description="Has execution trace")
    injects: bool = Field(description="Indicates if threat uses injections")
    known_threat: bool = Field(description="Indicates if known malware was detected")
    low_access: bool = Field(description="Indicates if threat uses low level access")
    malware_config: bool = Field(description="Indicates if malware config was extracted")
    mem_overrun: bool = Field(description="Indicates if overly high RAM usage was detected")
    multiprocessing: bool = Field(description="Indicates if threat uses multiprocessing")
    network_loader: bool = Field(description="Indicates if network download was detected")
    network_threats: bool = Field(description="Indicates if any network threats were detected")
    not_started: bool = Field(description="Indicates if submitted file execution failed")
    process_dump: bool = Field(description="Process memory dump availability")
    reboot: bool = Field(description="System reboot detected")
    service_luncher: bool = Field(description="New service registration detected")
    spam: bool = Field(description="Spam activity detected")
    static_detections: bool = Field(description="Static analysis detections")
    stealing: bool = Field(description="Information stealing detected")
    susp_struct: bool = Field(description="Suspicious structures detected")
    tor: bool = Field(description="TOR usage detected")
    uac_request: bool = Field(description="UAC request detected")


# Report models
class ReportVerdictDto(BaseModel):
    """Report verdict information."""

    score: float = Field(description="Numeric score of the analysis")
    threatLevel: float = Field(description="Threat level of the analysis")
    threatLevelText: ThreatLevelText = Field(description="Textual description of threat level")


class ReportSpecsDto(BaseModel):
    """Report specifications."""

    autoStart: bool = Field(default=False, description="Auto start flag")
    cpuOverrun: bool = Field(default=False, description="CPU overrun flag")
    crashedApps: bool = Field(default=False, description="Crashed apps flag")
    crashedTask: bool = Field(default=False, description="Crashed task flag")
    debugOutput: bool = Field(default=False, description="Debug output flag")
    executableDropped: bool = Field(default=False, description="Executable dropped flag")
    exploitable: bool = Field(default=False, description="Exploitable flag")
    injects: bool = Field(default=False, description="Injects flag")
    knownThreat: bool = Field(default=False, description="Known threat flag")
    lowAccess: bool = Field(default=False, description="Low access flag")
    malwareConfig: bool = Field(default=False, description="Malware config flag")
    memOverrun: bool = Field(default=False, description="Memory overrun flag")
    multiprocessing: bool = Field(default=False, description="Multiprocessing flag")
    networkLoader: bool = Field(default=False, description="Network loader flag")
    networkThreats: bool = Field(default=False, description="Network threats flag")
    notStarted: bool = Field(default=False, description="Not started flag")
    privEscalation: bool = Field(default=False, description="Privilege escalation flag")
    rebooted: bool = Field(default=False, description="Rebooted flag")
    serviceLauncher: bool = Field(default=False, description="Service launcher flag")
    spam: bool = Field(default=False, description="Spam flag")
    staticDetections: bool = Field(default=False, description="Static detections flag")
    stealing: bool = Field(default=False, description="Stealing flag")
    suspStruct: bool = Field(default=False, description="Suspicious structure flag")
    torUsed: bool = Field(default=False, description="TOR used flag")

    class Config:
        """Model configuration."""

        json_schema_extra = {
            "example": {
                "autoStart": False,
                "cpuOverrun": False,
                "crashedApps": False,
                "crashedTask": False,
                "debugOutput": False,
                "executableDropped": False,
                "exploitable": False,
                "injects": False,
                "knownThreat": False,
                "lowAccess": False,
                "malwareConfig": False,
                "memOverrun": False,
                "multiprocessing": False,
                "networkLoader": False,
                "networkThreats": False,
                "notStarted": False,
                "privEscalation": False,
                "rebooted": False,
                "serviceLauncher": False,
                "spam": False,
                "staticDetections": False,
                "stealing": False,
                "suspStruct": False,
                "torUsed": False,
            }
        }

    @model_validator(mode="after")  # type: ignore[misc]
    def validate_fields(self) -> "ReportSpecsDto":
        """Validate that all fields are properly set."""
        return self


class ReportMainObjectDto(BaseModel):
    """Main object information in report."""

    type: ObjectType = Field(description="Type of the main object")
    permanentUrl: str = Field(description="URL for downloading the main object")
    filename: Optional[str] = Field(None, description="Name of the main object file")
    basename: Optional[str] = Field(None, description="Submitted file name/url")
    url: Optional[str] = Field(None, description="Full URL")
    hashes: HashesApiDto = Field(description="Object hashes")
    info: Optional[Dict[str, Any]] = Field(None, description="Additional object information")


class ReportEnvironmentDto(BaseModel):
    """Environment information in report."""

    os: Dict[str, Any] = Field(description="Operating system information")
    software: List[Dict[str, Any]] = Field(description="Installed software information")
    hotfixes: Optional[List[str]] = Field(None, description="Installed hotfixes")


class ReportCountersDto(BaseModel):
    """Counters information in report."""

    processes: Dict[str, int] = Field(description="Process statistics")
    network: Dict[str, int] = Field(description="Network statistics")
    files: Dict[str, int] = Field(description="File statistics")
    registry: Dict[str, int] = Field(description="Registry statistics")
    synchronization: Dict[str, Any] = Field(description="Synchronization statistics")


class TaskReportDto(BaseModel):
    """Complete task report."""

    analysis: Dict[str, Any] = Field(description="Analysis information")
    environments: ReportEnvironmentDto = Field(description="Environment information")
    counters: ReportCountersDto = Field(description="Statistics counters")
    processes: List[Dict[str, Any]] = Field(description="Process information")
    network: Dict[str, Any] = Field(description="Network activity information")
    modified: Dict[str, Any] = Field(description="Modified files and registry")
    incidents: List[Dict[str, Any]] = Field(default=[], description="Detected incidents")
    mitre: List[Dict[str, Any]] = Field(default=[], description="MITRE ATT&CK information")
    malconf: List[Dict[str, Any]] = Field(default=[], description="Malware configuration")
    debugStrings: List[Dict[str, Any]] = Field(default=[], description="Debug strings")
    status: str = Field(description="Task completion status")
