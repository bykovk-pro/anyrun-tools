"""Example of hash lookup using TI Lookup API."""

import asyncio
import hashlib
import os
from pathlib import Path

from anyrun import AnyRunClient
from anyrun.utils.validation import validate_hash


def calculate_hashes(file_path: str) -> dict[str, str]:
    """Calculate MD5, SHA1 and SHA256 hashes of a file.

    Args:
        file_path: Path to file

    Returns:
        dict: Dictionary with hash values
    """
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
            sha1.update(chunk)
            sha256.update(chunk)

    return {
        "md5": md5.hexdigest(),
        "sha1": sha1.hexdigest(),
        "sha256": sha256.hexdigest(),
    }


async def lookup_hash(api_key: str, file_path: str) -> None:
    """Lookup file hashes using TI Lookup API.

    Args:
        api_key: ANY.RUN API key
        file_path: Path to file
    """
    # Calculate hashes
    print(f"Calculating hashes for: {file_path}")
    hashes = calculate_hashes(file_path)
    for hash_type, hash_value in hashes.items():
        print(f"{hash_type.upper()}: {hash_value}")

    # Validate hashes
    for hash_type, hash_value in hashes.items():
        validate_hash(hash_value, hash_type)

    # Initialize client
    async with AnyRunClient(api_key=api_key) as client:
        print("\nLooking up hashes...")

        # Look up each hash
        for hash_type, hash_value in hashes.items():
            try:
                result = await client.ti_lookup.lookup_hash(
                    hash_value=hash_value, hash_type=hash_type
                )

                print(f"\n{hash_type.upper()} lookup results:")
                if result.get("matches"):
                    for match in result["matches"]:
                        print(
                            f"\nMatch found:"
                            f'\n  First seen: {match.get("first_seen")}'
                            f'\n  Last seen: {match.get("last_seen")}'
                            f'\n  Detection rate: {match.get("detection_rate")}%'
                            f'\n  Classification: {match.get("classification")}'
                            f'\n  Tags: {", ".join(match.get("tags", []))}'
                        )
                else:
                    print("  No matches found")

            except Exception as e:
                print(f"\nError looking up {hash_type}: {str(e)}")


if __name__ == "__main__":
    # Get API key from environment
    api_key = os.getenv("ANYRUN_API_KEY")
    if not api_key:
        raise ValueError("ANYRUN_API_KEY environment variable is required")

    # Get file path from command line
    import sys

    if len(sys.argv) != 2:
        print("Usage: python lookup_hash.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Run lookup
    asyncio.run(lookup_hash(api_key, str(file_path)))
