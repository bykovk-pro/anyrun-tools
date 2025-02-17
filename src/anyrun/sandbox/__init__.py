"""Sandbox API client."""

__all__ = ["SandboxClient"]

"""Sandbox API client factory."""

from typing import Any, Dict, Optional, Type

from pydantic import HttpUrl

from .base import BaseSandboxClient
from .v1.client import SandboxClientV1


def create_sandbox_client(
    api_key: str,
    version: str = "v1",
    base_url: Optional[HttpUrl] = None,
    **kwargs: Any,
) -> BaseSandboxClient:
    """Create sandbox client instance.

    Args:
        api_key: ANY.RUN API key
        version: API version
        base_url: Base URL for API requests
        **kwargs: Additional client options

    Returns:
        BaseSandboxClient: Sandbox client instance

    Raises:
        ValueError: If version is not supported
    """
    clients: Dict[str, Type[BaseSandboxClient]] = {
        "v1": SandboxClientV1,
    }

    if version not in clients:
        raise ValueError(
            f"Unsupported API version: {version}. "
            f"Supported versions: {', '.join(clients.keys())}"
        )

    client_class = clients[version]
    return client_class(api_key=api_key, base_url=base_url, **kwargs)


__all__ = ["create_sandbox_client", "BaseSandboxClient"]
