# License: MIT
from importlib.metadata import version, PackageNotFoundError


try:
    __version__ = version("opsml")
except PackageNotFoundError:
    __version__ = "unknown"
