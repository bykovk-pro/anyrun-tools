"""Version information."""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import tomli


def get_version_from_pyproject() -> str:
    """Get version from pyproject.toml."""
    try:
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject = tomli.load(f)
        return f"{pyproject['project']['version']}-dev"
    except Exception:
        return "unknown-dev"


try:
    __version__ = version("anyrun-tools")
except PackageNotFoundError:
    __version__ = get_version_from_pyproject()
