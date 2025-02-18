"""Request types for Sandbox API v1."""

from enum import Enum


class RequestOSType(str, Enum):
    """Operating system type for requests."""

    WINDOWS = "windows"
    LINUX = "linux"


class RequestNetworkType(str, Enum):
    """Network type for requests."""

    DEFAULT = "default"
    TOR = "tor"
    VPN = "vpn"


class RequestGeoLocation(str, Enum):
    """Geographic location for requests."""

    FASTEST = "fastest"
    AU = "AU"
    BR = "BR"
    CH = "CH"
    DE = "DE"
    FR = "FR"
    GB = "GB"
    IT = "IT"
    KR = "KR"
    RU = "RU"
    US = "US"


class RequestPrivacyType(str, Enum):
    """Privacy type for requests."""

    PUBLIC = "public"
    BYLINK = "bylink"
    OWNER = "owner"
    BYTEAM = "byteam"
