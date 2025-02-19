"""TI Lookup API client implementation."""

from typing import Any, Dict, Optional

import httpx


class TILookupClient:
    """TI Lookup API client."""

    def __init__(
        self,
        api_key: str,
        version: str = "v1",
        cache_enabled: bool = True,
        timeout: int = 30,
    ) -> None:
        """Initialize TI Lookup client.

        Args:
            api_key: ANY.RUN API key
            version: API version
            cache_enabled: Enable caching
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.version = version
        self.cache_enabled = cache_enabled
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None

    async def lookup_hash(self, hash_value: str, hash_type: str) -> Dict[str, Any]:
        """Lookup hash in TI database.

        Args:
            hash_value: Hash value
            hash_type: Hash type (md5, sha1, sha256)

        Returns:
            Dict[str, Any]: Lookup results

        Raises:
            NotImplementedError: This is a stub
        """
        raise NotImplementedError("TI Lookup API is not implemented yet")

    async def close(self) -> None:
        """Close HTTP client."""
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    async def __aenter__(self) -> "TILookupClient":
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context."""
        await self.close()
