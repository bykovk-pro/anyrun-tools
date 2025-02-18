"""Sandbox API client."""

from typing import Dict, Optional

from pydantic import HttpUrl

from .base import BaseSandboxClient
from .v1.client import SandboxClientV1


def create_sandbox_client(
    api_key: str,
    version: str = "v1",
    base_url: Optional[HttpUrl] = None,
    timeout: Optional[int] = None,
    verify_ssl: bool = True,
    user_agent: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
) -> BaseSandboxClient:
    """Create sandbox client instance.

    Args:
        api_key: ANY.RUN API key
        version: API version
        base_url: Base URL for API requests
        timeout: Request timeout in seconds
        verify_ssl: Verify SSL certificates
        user_agent: User agent string
        headers: Additional headers

    Returns:
        BaseSandboxClient: Sandbox client instance

    Raises:
        ValueError: If version is not supported
    """
    if version == "v1":
        return SandboxClientV1(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            verify_ssl=verify_ssl,
            user_agent=user_agent,
            headers=headers,
        )
    raise ValueError(f"Unsupported version: {version}")


__all__ = ["create_sandbox_client", "BaseSandboxClient"]
