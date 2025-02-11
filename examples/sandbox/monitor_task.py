"""Example of task monitoring using Sandbox API."""

import asyncio
import json
import os
from datetime import datetime

from anyrun import AnyRunClient


async def monitor_task(api_key: str, task_id: str) -> None:
    """Monitor analysis task using Sandbox API.

    Args:
        api_key: ANY.RUN API key
        task_id: Analysis task ID
    """
    # Initialize client
    async with AnyRunClient(api_key=api_key) as client:
        print(f"Starting monitoring for task: {task_id}")
        print("Waiting for updates...")

        try:
            # Monitor task with improved endpoint
            async for update in client.sandbox.get_analysis_monitor(task_id):
                if update.get("error"):
                    print(f'Error: {update["data"].get("message")}')
                    break

                data = update["data"]
                timestamp = datetime.now().strftime("%H:%M:%S")

                # Process status update
                if "status" in data:
                    print(f'\n[{timestamp}] Status: {data["status"]}')

                # Process process creation
                if "process" in data:
                    proc = data["process"]
                    print(
                        f"\n[{timestamp}] New process:"
                        f'\n  PID: {proc.get("pid")}'
                        f'\n  Name: {proc.get("name")}'
                        f'\n  Path: {proc.get("path")}'
                        f'\n  Command: {proc.get("cmdline")}'
                    )

                # Process network activity
                if "network" in data:
                    net = data["network"]
                    print(
                        f"\n[{timestamp}] Network activity:"
                        f'\n  Type: {net.get("type")}'
                        f'\n  Protocol: {net.get("protocol")}'
                        f'\n  Source: {net.get("src_ip")}:{net.get("src_port")}'
                        f'\n  Destination: {net.get("dst_ip")}:{net.get("dst_port")}'
                    )

                # Process file operations
                if "filesystem" in data:
                    fs = data["filesystem"]
                    print(
                        f"\n[{timestamp}] File operation:"
                        f'\n  Operation: {fs.get("operation")}'
                        f'\n  Path: {fs.get("path")}'
                    )

                # Process registry operations (Windows only)
                if "registry" in data:
                    reg = data["registry"]
                    print(
                        f"\n[{timestamp}] Registry operation:"
                        f'\n  Operation: {reg.get("operation")}'
                        f'\n  Path: {reg.get("path")}'
                        f'\n  Value: {reg.get("value")}'
                    )

                # Save raw update for debugging
                with open(f"{task_id}_updates.jsonl", "a") as f:
                    f.write(json.dumps(data) + "\n")

        except asyncio.CancelledError:
            print("\nMonitoring cancelled")
        except Exception as e:
            print(f"\nError during monitoring: {str(e)}")

        print("\nMonitoring finished")
        print(f"Updates saved to: {task_id}_updates.jsonl")


if __name__ == "__main__":
    # Get API key from environment
    api_key = os.getenv("ANYRUN_API_KEY")
    if not api_key:
        raise ValueError("ANYRUN_API_KEY environment variable is required")

    # Get task ID from command line
    import sys

    if len(sys.argv) != 2:
        print("Usage: python monitor_task.py <task_id>")
        sys.exit(1)

    task_id = sys.argv[1]

    # Run monitoring
    try:
        asyncio.run(monitor_task(api_key, task_id))
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
