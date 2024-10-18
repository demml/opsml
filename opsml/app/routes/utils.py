# pylint: disable=protected-access
# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from pathlib import Path
from typing import Any, Optional

from streaming_form_data.targets import FileTarget

from opsml.helpers.logging import ArtifactLogger
from opsml.storage.client import LocalStorageClient, StorageClient
from opsml.types import RegistryType

logger = ArtifactLogger.get_logger()


def get_registry_type_from_table(
    table_name: Optional[str] = None,
    registry_type: Optional[str] = None,
) -> str:
    """
    This is a hack to get the registry type from the table name.
    This is needed to maintain backwards compatibility in V1
    """

    if table_name is not None:
        for _registry_type in RegistryType:
            if _registry_type.value.upper() in table_name:
                return _registry_type.value

    if registry_type is not None:
        return registry_type

    raise ValueError("Could not determine registry type")


class MaxBodySizeException(Exception):
    def __init__(self, body_len: int):
        self.body_len = body_len


class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.body_len = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes) -> None:
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=self.body_len)


class ExternalFileTarget(FileTarget):  # type: ignore[misc]
    def __init__(  # pylint: disable=keyword-arg-before-vararg
        self,
        write_path: Path,
        storage_client: StorageClient,
        allow_overwrite: bool = True,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(filename=write_path.name, allow_overwrite=allow_overwrite, *args, **kwargs)

        self.storage_client = storage_client
        self.write_path = write_path

        if isinstance(self.storage_client, LocalStorageClient):
            self.write_path.parent.mkdir(parents=True, exist_ok=True)

    def on_start(self) -> None:
        self._fd = self.storage_client.open(self.write_path, self._mode)


def calculate_file_size(size: int) -> str:
    """Calculates file size in human readable format
    Args:
        size:
            File size in bytes
    Returns:
        Human readable file size
    """
    if size < 1024:
        return f"{size} B"
    if size < 1024**2:
        return f"{size / 1024:.2f} KB"
    if size < 1024**3:
        return f"{size / 1024 ** 2:.2f} MB"

    return f"{size / 1024 ** 3:.2f} GB"
