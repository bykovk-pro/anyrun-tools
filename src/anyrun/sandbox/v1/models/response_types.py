"""Response types for Sandbox API v1."""

from enum import Enum


class ResponseOSType(str, Enum):
    """Operating system type from responses."""

    WINDOWS = "Windows"
    LINUX = "Linux"


class ResponseNetworkType(str, Enum):
    """Network type from responses."""

    DEFAULT = "default"
    TOR = "tor"
    VPN = "vpn"
    UNLIMITED = "unlimited"


class ResponseGeoLocation(str, Enum):
    """Geographic location from responses."""

    FASTEST = "fastest"
    EMPTY = ""
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


class ResponsePrivacyType(str, Enum):
    """Privacy type from responses."""

    PUBLIC = "public"
    BYLINK = "bylink"
    OWNER = "owner"
    BYTEAM = "byteam"
