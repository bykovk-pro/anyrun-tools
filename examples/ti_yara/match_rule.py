"""Example of YARA rule matching using TI YARA API."""

import asyncio
import os
from pathlib import Path

from anyrun import AnyRunClient


async def match_rule(api_key: str, rule_path: str) -> None:
    """Match YARA rule against public samples.

    Args:
        api_key: ANY.RUN API key
        rule_path: Path to YARA rule file
    """
    # Read rule content
    with open(rule_path) as f:
        rule_content = f.read()

    print(f"Using YARA rule from: {rule_path}")
    print("Rule content:")
    print("=" * 40)
    print(rule_content)
    print("=" * 40)

    # Initialize client
    async with AnyRunClient(api_key=api_key) as client:
        print("\nMatching rule against public samples...")

        try:
            result = await client.ti_yara.match_rule(
                rule_content=rule_content, target_type="public"
            )

            if result.get("matches"):
                print(f'\nFound {len(result["matches"])} matches:')
                for match in result["matches"]:
                    print(
                        f"\nMatch details:"
                        f'\n  Sample hash: {match.get("hash")}'
                        f'\n  Rule name: {match.get("rule_name")}'
                        f'\n  First seen: {match.get("first_seen")}'
                        f'\n  Last seen: {match.get("last_seen")}'
                        f'\n  Tags: {", ".join(match.get("tags", []))}'
                    )

                    # Print matched strings
                    if match.get("strings"):
                        print("\n  Matched strings:")
                        for string in match["strings"]:
                            print(f" - {string}")

            else:
                print("\nNo matches found")

        except Exception as e:
            print(f"\nError matching rule: {str(e)}")


if __name__ == "__main__":
    # Get API key from environment
    api_key = os.getenv("ANYRUN_API_KEY")
    if not api_key:
        raise ValueError("ANYRUN_API_KEY environment variable is required")

    # Get rule path from command line
    import sys

    if len(sys.argv) != 2:
        print("Usage: python match_rule.py <rule_path>")
        sys.exit(1)

    rule_path = Path(sys.argv[1])
    if not rule_path.exists():
        raise FileNotFoundError(f"Rule file not found: {rule_path}")

    # Run matching
    asyncio.run(match_rule(api_key, str(rule_path)))
