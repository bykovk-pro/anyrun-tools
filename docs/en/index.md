# ANY.RUN Tools

Python SDK for ANY.RUN APIs

## Overview

ANY.RUN Tools is a Python library that provides a convenient way to interact with ANY.RUN APIs:

- **Sandbox API** - Submit files and URLs for analysis, monitor analysis progress, and get results
- **TI Lookup API** - Look up file hashes in the ANY.RUN threat intelligence database
- **TI YARA API** - Match YARA rules against public and private samples

## Features

- ✨ Modern async/await API
- 🚀 Type hints and data validation with Pydantic
- 💾 Built-in caching support
- 🔄 Automatic retries with exponential backoff
- 🚦 Rate limiting
- 📝 Comprehensive documentation
- 🧪 Extensive test coverage

## Quick Start

```python
from anyrun import AnyRunClient

# Initialize client
async with AnyRunClient(api_key="your-api-key") as client:
    # Submit file for analysis
    response = await client.sandbox.analyze(
        obj_type="file",
        file=b"file_content",
        env_os="windows",
        env_version="10"
    )

    task_id = response["data"]["task_id"]

    # Monitor analysis status
    async for update in client.sandbox.get_analysis_status(task_id):
        print(f"Status: {update['status']}")

    # Get analysis results
    result = await client.sandbox.get_analysis(task_id)
    print(f"Analysis score: {result['data']['score']}")
```

## Installation

```bash
pip install anyrun-tools
```

## Requirements

- Python 3.8+
- `httpx` - For making HTTP requests
- `pydantic` - For data validation
- `aioredis` (optional) - For Redis caching support

## Documentation

For detailed documentation, please visit:

- [Installation](getting-started/installation.md)
- [Configuration](getting-started/configuration.md)
- [Quick Start](getting-started/quickstart.md)
- [API Reference](api-reference/client.md)
- [Examples](examples/sandbox/file-analysis.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](contributing.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/anyrun/anyrun-tools/blob/main/LICENSE) file for details.
