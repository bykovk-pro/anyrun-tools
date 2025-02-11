# Installation

## Requirements

Before installing ANY.RUN Tools, make sure you have:

- Python 3.8 or higher
- pip (Python package installer)
- API key from [ANY.RUN](https://any.run)

## Installing with pip

The simplest way to install ANY.RUN Tools is using pip:

```bash
pip install anyrun-tools
```

This will install the package and all required dependencies.

## Installing from source

If you want to install the latest development version or contribute to the project, you can install from source:

```bash
git clone https://github.com/anyrun/anyrun-tools.git
cd anyrun-tools
pip install -e .
```

## Optional dependencies

ANY.RUN Tools has several optional dependencies that provide additional features:

- `redis` - For Redis caching support:
  ```bash
  pip install anyrun-tools[redis]
  ```

- `dev` - For development (includes testing and documentation tools):
  ```bash
  pip install anyrun-tools[dev]
  ```

- `docs` - For building documentation:
  ```bash
  pip install anyrun-tools[docs]
  ```

## Verifying installation

You can verify that ANY.RUN Tools is installed correctly by running Python and importing the package:

```python
import anyrun
print(anyrun.__version__)
```

## Next steps

- [Configure the client](configuration.md)
- [Quick start guide](quickstart.md)
- [API reference](../api-reference/client.md)

## Troubleshooting

### Common issues

1. **ImportError: No module named 'anyrun'**
   - Make sure you have installed the package correctly
   - Check that you're using the correct Python environment

2. **Version conflicts**
   - Try installing in a fresh virtual environment
   - Update your dependencies to their latest versions

3. **Installation fails**
   - Make sure you have the latest pip version: `pip install --upgrade pip`
   - Check your Python version: `python --version`

### Getting help

If you encounter any issues during installation:

1. Check our [GitHub Issues](https://github.com/anyrun/anyrun-tools/issues) for similar problems
2. Create a new issue if your problem hasn't been reported
3. Include your:
   - Python version
   - Installation method
   - Full error message
   - Operating system
