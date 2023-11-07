# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from pathlib import Path
from typing import Any, Dict, Optional

from streaming_form_data.targets import FileTarget

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.cards.types import RegistryType
from opsml.registry.storage.storage_system import LocalStorageClient, StorageClientType

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


def get_real_path(current_path: str, proxy_root: str, storage_root: str) -> str:
    new_path = current_path.replace(proxy_root, f"{storage_root}/")
    return new_path


def replace_proxy_root(
    card: Dict[str, Any],
    storage_root: str,
    proxy_root: str,
) -> Dict[str, Any]:
    for name, value in card.items():
        if "uri" in name:
            if isinstance(value, str):
                real_path = get_real_path(
                    current_path=value,
                    proxy_root=proxy_root,
                    storage_root=storage_root,
                )
                card[name] = real_path

        if isinstance(value, dict):
            replace_proxy_root(
                card=value,
                storage_root=storage_root,
                proxy_root=proxy_root,
            )

    return card


class MaxBodySizeException(Exception):
    def __init__(self, body_len: int):
        self.body_len = body_len


class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.body_len = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes):
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=self.body_len)


class ExternalFileTarget(FileTarget):
    def __init__(  # pylint: disable=keyword-arg-before-vararg
        self,
        filename: str,
        write_path: str,
        storage_client: StorageClientType,
        allow_overwrite: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(filename=filename, allow_overwrite=allow_overwrite, *args, **kwargs)

        self.storage_client = storage_client
        self.write_path = write_path
        self.filepath = f"{self.write_path}/{filename}"
        self._create_base_path()

    def _create_base_path(self):
        if isinstance(self.storage_client, LocalStorageClient):
            Path(self.write_path).mkdir(parents=True, exist_ok=True)

    def on_start(self):
        self._fd = self.storage_client.open(self.filepath, self._mode)
