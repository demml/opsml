import os
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel


class StorageClientInfo(BaseModel):
    storage_type: str = "local"
    storage_url: str = os.path.expanduser("~")


class GcsStorageClientInfo(StorageClientInfo):
    credentials: Optional[Any]
    gcp_project: str


class NoneStorageClientInfo(StorageClientInfo):
    storage_type = "None"
    storage_url = "None"


StorageInfo = Union[StorageClientInfo, GcsStorageClientInfo]

PATH_PREFIX = "opsml"


class ApiRoutes(str, Enum):
    CHECK_UID = f"{PATH_PREFIX}/check_uid"
    SET_VERSION = f"{PATH_PREFIX}/set_version"
    LIST_CARDS = f"{PATH_PREFIX}/list_cards"
    STORAGE_PATH = f"{PATH_PREFIX}/storage_path"
    ADD_RECORD = f"{PATH_PREFIX}/add_record"
    UPDATE_RECORD = f"{PATH_PREFIX}/update_record"
    QUERY_RECORD = f"{PATH_PREFIX}/query_record"
