import os
from typing import Any, Optional, Union

from pydantic import BaseModel


class StorageClientSettings(BaseModel):
    storage_type: str = "local"
    storage_uri: str = os.path.expanduser("~")


class GcsStorageClientSettings(StorageClientSettings):
    credentials: Optional[Any]
    gcp_project: str


StorageSettings = Union[StorageClientSettings, GcsStorageClientSettings]
