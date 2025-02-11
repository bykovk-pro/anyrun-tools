"""Example of file analysis using Sandbox API."""

import asyncio
import os
from pathlib import Path

from anyrun import AnyRunClient
from anyrun.sandbox.v1.models.analysis import (
    BitnessType,
    Browser,
    EnvType,
    ObjectType,
    OSType,
    PrivacyType,
    StartFolder,
    WindowsVersion,
)


async def analyze_file(api_key: str, file_path: str) -> None:
    """Analyze file using Sandbox API.

    Args:
        api_key: ANY.RUN API key
        file_path: Path to file for analysis
    """
    # Initialize client
    async with AnyRunClient(api_key=api_key) as client:
        # Read file content
        with open(file_path, "rb") as f:
            file_content = f.read()

        print(f"Analyzing file: {file_path}")
        print(f"File size: {len(file_content)} bytes")

        # Submit analysis
        response = await client.sandbox.analyze(
            obj_type=ObjectType.FILE,
            file=file_content,
            env_os=OSType.WINDOWS,
            env_version=WindowsVersion.WIN10,
            env_bitness=BitnessType.X64,
            env_type=EnvType.CLEAN,
            obj_ext_browser=Browser.CHROME,
            obj_ext_startfolder=StartFolder.TEMP,
            opt_privacy_type=PrivacyType.BYLINK,
        )

        task_id = response["data"]["task_id"]
        print("\nAnalysis submitted successfully!")
        print(f"Task ID: {task_id}")

        # Monitor analysis status
        print("\nMonitoring analysis status...")
        async for update in client.sandbox.get_analysis_status(task_id):
            status = update.get("status")
            if status == "completed":
                print("\nAnalysis completed!")
                break
            elif status == "failed":
                print(f'\nAnalysis failed: {update.get("error")}')
                break
            else:
                print(f"Status: {status}")

        # Get analysis results
        print("\nGetting analysis results...")
        result = await client.sandbox.get_analysis(task_id)
        print(f'Analysis score: {result["data"].get("score", "N/A")}')
        print(f"Analysis report: https://app.any.run/tasks/{task_id}")


if __name__ == "__main__":
    # Get API key from environment
    api_key = os.getenv("ANYRUN_API_KEY")
    if not api_key:
        raise ValueError("ANYRUN_API_KEY environment variable is required")

    # Get sample file path
    file_path = Path(__file__).parent / "samples" / "sample.exe"
    if not file_path.exists():
        raise FileNotFoundError(f"Sample file not found: {file_path}")

    # Run analysis
    asyncio.run(analyze_file(api_key, str(file_path)))
