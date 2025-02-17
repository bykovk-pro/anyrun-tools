# ANY.RUN Tools

[![Tests](https://github.com/bykovk-pro/anyrun-tools/actions/workflows/test.yml/badge.svg)](https://github.com/bykovk-pro/anyrun-tools/actions/workflows/test.yml)
[![Documentation](https://github.com/bykovk-pro/anyrun-tools/actions/workflows/docs.yml/badge.svg)](https://github.com/bykovk-pro/anyrun-tools/actions/workflows/docs.yml)
[![PyPI version](https://badge.fury.io/py/anyrun-tools.svg)](https://badge.fury.io/py/anyrun-tools)
[![Python versions](https://img.shields.io/pypi/pyversions/anyrun-tools.svg)](https://pypi.org/project/anyrun-tools/)
[![License](https://img.shields.io/github/license/bykovk-pro/anyrun-tools.svg)](https://github.com/bykovk-pro/anyrun-tools/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)
[![Downloads](https://static.pepy.tech/badge/anyrun-tools)](https://pepy.tech/project/anyrun-tools)
[![codecov](https://codecov.io/gh/bykovk-pro/anyrun-tools/branch/main/graph/badge.svg)](https://codecov.io/gh/bykovk-pro/anyrun-tools)

Python SDK for ANY.RUN APIs

## Features

- ✨ Modern async/await API
- 🚀 Type hints and data validation with Pydantic
- 💾 Built-in caching support (memory and Redis)
- 🔄 Automatic retries with exponential backoff
- 🚦 Rate limiting
- 📝 Comprehensive documentation
- 🧪 Extensive test coverage
- 🐍 Supports Python 3.8-3.12

## Installation

```bash
# Basic installation
pip install anyrun-tools

# With Redis caching support
pip install anyrun-tools[redis]

# With all optional dependencies
pip install anyrun-tools[all]
```

## Quick Start

```python
from anyrun import AnyRunClient

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

## Available APIs

### Sandbox API
- Submit files and URLs for analysis
- Monitor analysis progress in real-time
- Get detailed analysis results
- Manage analysis tasks

### TI Lookup API (coming soon)
- Look up file hashes
- Get threat intelligence data
- Check indicators of compromise

### TI YARA API (coming soon)
- Match YARA rules against samples
- Get matching details
- Manage YARA rules

## Documentation

For detailed documentation, please visit [https://bykovk-pro.github.io/anyrun-tools](https://bykovk-pro.github.io/anyrun-tools)

- [Installation](https://bykovk-pro.github.io/anyrun-tools/getting-started/installation/)
- [Configuration](https://bykovk-pro.github.io/anyrun-tools/getting-started/configuration/)
- [Quick Start](https://bykovk-pro.github.io/anyrun-tools/getting-started/quickstart/)
- [API Reference](https://bykovk-pro.github.io/anyrun-tools/api-reference/client/)
- [Examples](https://bykovk-pro.github.io/anyrun-tools/examples/sandbox/file-analysis/)

## Development

```bash
# Clone the repository
git clone https://github.com/bykovk-pro/anyrun-tools.git
cd anyrun-tools

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Build documentation
pip install -e .[docs]
mkdocs serve
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

If you discover a security vulnerability within ANY.RUN Tools, please send an e-mail to Kirill Bykov via [bykovk@anyrun.tools](mailto:bykovk@anyrun.tools). All security vulnerabilities will be promptly addressed.
