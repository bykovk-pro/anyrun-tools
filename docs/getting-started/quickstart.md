# Quick Start

This guide will help you get started with ANY.RUN Tools quickly.

## Prerequisites

Before you begin, make sure you have:

1. Installed ANY.RUN Tools:
   ```bash
   pip install anyrun-tools
   ```

2. Obtained an API key from [ANY.RUN](https://any.run)

## Basic usage

### Initialize client

```python
from anyrun import AnyRunClient

# Using context manager (recommended)
async with AnyRunClient(api_key="your-api-key") as client:
    # Use client here
    ...

# Or manually
client = AnyRunClient(api_key="your-api-key")
try:
    # Use client here
    ...
finally:
    await client.close()
```

### Sandbox API examples

#### Analyze file

```python
# Submit file for analysis
response = await client.sandbox.analyze(
    obj_type="file",
    file=b"file_content",
    env_os="windows",
    env_version="10",
    env_bitness="64",
    env_type="clean"
)

task_id = response["data"]["task_id"]

# Monitor analysis status
async for update in client.sandbox.get_analysis_status(task_id):
    print(f"Status: {update['status']}")

# Get analysis results
result = await client.sandbox.get_analysis(task_id)
print(f"Analysis score: {result['data']['score']}")
```

#### Analyze URL

```python
# Submit URL for analysis
response = await client.sandbox.analyze(
    obj_type="url",
    obj_url="https://example.com",
    env_os="windows",
    env_version="10"
)

task_id = response["data"]["task_id"]
```

#### Monitor task in real-time

```python
# Monitor task with detailed updates
async for update in client.sandbox.get_analysis_monitor(task_id):
    if "process" in update["data"]:
        proc = update["data"]["process"]
        print(f"New process: {proc['name']} (PID: {proc['pid']})")

    if "network" in update["data"]:
        net = update["data"]["network"]
        print(f"Network: {net['protocol']} {net['dst_ip']}:{net['dst_port']}")
```

### TI Lookup API examples

#### Look up hash

```python
# Look up file hash
result = await client.ti_lookup.lookup_hash(
    hash_value="0123456789abcdef0123456789abcdef",
    hash_type="md5"
)

if result["matches"]:
    for match in result["matches"]:
        print(f"Match found: {match['classification']}")
```

### TI YARA API examples

#### Match rule

```python
# Match YARA rule
rule_content = """
rule suspicious_behavior {
    strings:
        $s1 = "malicious" nocase
    condition:
        any of them
}
"""

result = await client.ti_yara.match_rule(
    rule_content=rule_content,
    target_type="public"
)

if result["matches"]:
    for match in result["matches"]:
        print(f"Match found: {match['hash']}")
```

## Error handling

```python
from anyrun.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ServerError,
)

try:
    result = await client.sandbox.analyze(...)
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limit exceeded. Try again in {e.retry_after} seconds")
except ServerError:
    print("Server error occurred")
except APIError as e:
    print(f"API error: {str(e)}")
```

## Using caching

```python
# Enable Redis caching
client = AnyRunClient(
    api_key="your-api-key",
    cache_enabled=True,
    cache_backend="redis",
    cache_config={
        "url": "redis://localhost:6379"
    }
)

# Cached requests
result1 = await client.sandbox.get_analysis(task_id)  # Makes API request
result2 = await client.sandbox.get_analysis(task_id)  # Uses cache
```

## Rate limiting

```python
# Configure rate limiting
client = AnyRunClient(
    api_key="your-api-key",
    rate_limit_enabled=True,
    rate_limit_strategy="wait"  # Will wait when limit is reached
)

# Requests will be rate limited automatically
for file in files:
    await client.sandbox.analyze(
        obj_type="file",
        file=file,
        env_os="windows",
        env_version="10"
    )
```

## Next steps

- [Configuration guide](configuration.md) - Learn about all configuration options
- [API reference](https://any.run/api-documentation/) - Detailed API documentation
- [Examples](https://github.com/bykovk-pro/anyrun-tools/tree/main/examples) - More code examples
