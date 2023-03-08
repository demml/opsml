import os
from typing import Any, Optional, Union

from pydantic import BaseModel


class StorageClientInfo(BaseModel):
    storage_type: str = "local"
    storage_url: str = os.path.expanduser("~")


class GcsStorageClientInfo(StorageClientInfo):
    credentials: Optional[Any]
    gcp_project: str


StorageInfo = Union[StorageClientInfo, GcsStorageClientInfo]
