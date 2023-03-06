from typing import Optional, Any, Union
import os
from pydantic import BaseModel


class StorageClientInfo(BaseModel):
    storage_type: str = "local"
    storage_url: str = os.path.expanduser("~")


class GcsStorageClientInfo(StorageClientInfo):
    credentials: Optional[Any]
    gcp_project: str


StorageInfo = Union[StorageClientInfo, GcsStorageClientInfo]
