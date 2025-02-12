"""Version information."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("anyrun-tools")
except PackageNotFoundError:
    __version__ = "unknown" 