from pathlib import Path
from typing import List

from ..core import OpsmlStorageSettings

class StorageType:
    Google: "StorageType"
    Local: "StorageType"
    Aws: "StorageType"
    Azure: "StorageType"

class FileInfo:
    name: str
    size: int
    object_type: str
    created: str
    suffix: str

class FileSystemStorage:
    def __init__(self, settings: OpsmlStorageSettings) -> None:
        """Initialize the storage system.

        Args:
            settings: The settings for the storage system.
        """

    def name(self) -> str:
        """Get the name of the storage system.

        Returns:
            The name of the storage system.
        """

    def storage_type(self) -> StorageType:
        """Get the storage type.

        Returns:
            The storage type.
        """

    def find(self, path: Path) -> List[str]:
        """Check if a file exists in the storage system.

        Args:
            path (Path):
                The path to the file.

        Returns:
            A list of file names.
        """

    def find_info(self, path: Path) -> List[FileInfo]:
        """Get file information.

        Args:
            path (Path):
                The path to the file.

        Returns:
            A list of file information.
        """

    def get(self, lpath: Path, rpath: Path, recursive=False) -> None:
        """Download file(s) from the storage system.

        Args:
            lpath (Path):
                The local path to save the file.
            rpath (Path):
                The remote path to the file.
            recursive (bool):
                Download files recursively.
        """

    def put(self, lpath: Path, rpath: Path, recursive=False) -> None:
        """Upload file(s) to the storage system.

        Args:
            lpath (Path):
                The local path to the file.
            rpath (Path):
                The remote path to save the file.
            recursive (bool):
                Upload files recursively.
        """

    def rm(self, path: Path, recursive=False) -> None:
        """Remove file(s) from the storage system.

        Args:
            path (Path):
                The path to the file.
            recursive (bool):
                Remove files recursively.
        """

    def exists(self, path: Path) -> bool:
        """Check if a file exists in the storage system.

        Args:
            path (Path):
                The path to the file.

        Returns:
            True if the file exists, otherwise False.
        """

    def generate_presigned_url(self, path: Path, expiration: int) -> str:
        """Generate a presigned URL.

        Args:
            path (Path):
                The path to the file.
            expiration (int):
                The expiration time in seconds.

        Returns:
            The presigned URL.
        """
