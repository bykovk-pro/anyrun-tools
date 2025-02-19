"""Common models for Sandbox API v1."""

from enum import Enum

from pydantic import BaseModel, Field


class ThreatLevelText(str, Enum):
    """Threat level text."""

    UNDETECTED = "No threats detected"
    SUSPICIOUS = "Suspicious activity"
    MALICIOUS = "Malicious activity"


class PrivacyType(str, Enum):
    """Privacy type."""

    PUBLIC = "public"
    BYLINK = "bylink"
    OWNER = "owner"
    BYTEAM = "byteam"


class HashesApiDto(BaseModel):
    """Object's hashes."""

    md5: str = Field(pattern="^[0-9a-f]{32}$", description="MD5 hash string")
    sha1: str = Field(pattern="^[0-9a-f]{40}$", description="SHA1 hash string")
    sha256: str = Field(pattern="^[0-9a-f]{64}$", description="SHA256 hash string")
    ssdeep: str = Field(description="SSDEEP hash string")
