"""Example script to test ANY.RUN API functionality."""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional
import traceback

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
from pydantic import HttpUrl


def json_serial(obj: Any) -> str:
    """JSON serializer for objects not serializable by default json code.

    Args:
        obj: Object to serialize

    Returns:
        str: Serialized object
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, HttpUrl):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


async def test_api() -> None:
    """Test ANY.RUN API functionality."""
    # Get API key from environment
    api_key = os.getenv("ANYRUN_API_KEY")
    if not api_key:
        raise ValueError("ANYRUN_API_KEY environment variable is not set")

    print(f"Using API key: {api_key}")

    # Initialize client with v1 version of sandbox API
    client = AnyRunClient(
        api_key=api_key,
        sandbox_version="v1",
        cache_enabled=False,  # Disable cache for testing
    )

    try:
        # 1. Get user info and limits
        print("\n1. Getting user info and limits...")
        user_info = await client.sandbox.user_info()
        print("User info response:")
        print(json.dumps(user_info.model_dump(), indent=2))

        # 2. Get user presets
        print("\n2. Getting user presets...")
        presets = await client.sandbox.get_user_presets()
        print("User presets response:")
        print(json.dumps(presets.model_dump(), indent=2, default=json_serial))

        # 3. Get available environments
        print("\n3. Getting available environments...")
        environments = await client.sandbox.get_environment()
        print("Environments response:")
        print(json.dumps(environments.model_dump(), indent=2))

        # 4. Submit URL for analysis
        print("\n4. Submitting URL for analysis...")
        try:
            url_analysis = await client.sandbox.analyze_url(
                url="https://anyrun.tools",
                env_os=OSType.WINDOWS,
                env_version=WindowsVersion.WIN10,
                env_bitness=BitnessType.X64,
                env_type=EnvType.COMPLETE,
                obj_ext_browser=Browser.EDGE,
                obj_ext_startfolder=StartFolder.TEMP,
                opt_privacy_type=PrivacyType.BYLINK,
            )
            print("Analysis response:")
            print(json.dumps(url_analysis.model_dump(), indent=2))

            # Используем taskid из ответа
            task_id = url_analysis.data.taskid or url_analysis.data.task_id
            if task_id:
                print(f"\nAnalysis submitted successfully! Task ID: {task_id}")
                print(
                    f"You can view the analysis at: https://app.any.run/tasks/{task_id}"
                )

                # 5. Monitor analysis status
                print("\n5. Monitoring analysis status...")
                print("Waiting for status updates (press Ctrl+C to stop)...")
                try:
                    is_running = False
                    time_added = False
                    task_stopped = False

                    async for update in client.sandbox.get_analysis_status_stream(task_id):
                        print(f"Status update: {json.dumps(update, indent=2)}")

                        # Check if task is running
                        if update.get("task", {}).get("status") == 50 and not is_running:  # Running
                            is_running = True
                            print("\nAnalysis is running. Waiting 10 seconds before adding time...")
                            await asyncio.sleep(10)

                            # 6. Add time to analysis
                            if not time_added:
                                print("\n6. Adding time to analysis...")
                                try:
                                    add_time = await client.sandbox.add_analysis_time(task_id)
                                    time_added = True
                                    print("Successfully added time to analysis")
                                except Exception as e:
                                    print(f"Failed to add time to analysis: {str(e)}")
                                    traceback.print_exc()

                            print("\nWaiting 10 seconds before stopping analysis...")
                            await asyncio.sleep(10)

                            # 7. Stop analysis
                            if not task_stopped:
                                print("\n7. Stopping analysis...")
                                try:
                                    stop = await client.sandbox.stop_analysis(task_id)
                                    task_stopped = True
                                    print("Successfully stopped analysis")
                                except Exception as e:
                                    print(f"Failed to stop analysis: {str(e)}")
                                    traceback.print_exc()
                            break

                        # If analysis is completed or failed, stop monitoring
                        if update.get("completed") or update.get("error"):
                            break

                except KeyboardInterrupt:
                    print("\nStatus monitoring stopped by user")

                print("\nWaiting 10 seconds for analysis to finish...")
                await asyncio.sleep(10)

                # 8. Get analysis result
                print("\n8. Getting analysis result...")
                result = await client.sandbox.get_analysis(task_id)
                print("Analysis result:")
                print(json.dumps(result.model_dump(), indent=2))

                # 9. List recent analyses
                print("\n9. Listing recent analyses...")
                analyses = await client.sandbox.list_analyses(limit=5)
                print("Recent analyses:")
                print(json.dumps(analyses.model_dump(), indent=2))

                # 10. Delete analysis
                print("\n10. Deleting analysis...")
                try:
                    # Используем uuid из первоначального ответа
                    delete = await client.sandbox.delete_analysis(task_id)
                    print("\nDelete response:")
                    print(json.dumps(delete.model_dump(), indent=2))
                    
                    # Проверяем список анализов после удаления
                    print("\nAnalyses after deletion:")
                    analyses_after = await client.sandbox.list_analyses(limit=5)
                    print(json.dumps(analyses_after.model_dump(), indent=2))
                except Exception as e:
                    print(f"Failed to delete analysis: {str(e)}")
                    traceback.print_exc()

            else:
                print("Warning: No task_id in response")
                print("Raw response data:")
                print(json.dumps(url_analysis.data.model_dump(), indent=2))

        except Exception as e:
            print(f"Error during analysis submission: {str(e)}")
            if hasattr(e, "response"):
                print(f"Response status: {e.response.status_code}")
                print(f"Response headers: {dict(e.response.headers)}")
                print(f"Response content: {e.response.text}")
            raise

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_api())
