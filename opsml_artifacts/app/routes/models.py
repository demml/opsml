from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class HealthCheckResult(BaseModel):
    is_alive: bool


class DebugResponse(BaseModel):
    url: str
    storage: str
    app_env: str
    proxy_root: Optional[str]
    is_proxy: Optional[bool]


class StorageSettingsResponse(BaseModel):
    storage_type: str
    storage_uri: str
    proxy: bool = False


class VersionRequest(BaseModel):
    name: str
    team: str
    version_type: str
    table_name: str


class VersionResponse(BaseModel):
    version: str


class UidExistsRequest(BaseModel):
    uid: str
    table_name: str


class UidExistsResponse(BaseModel):
    uid_exists: bool


class ListRequest(BaseModel):
    name: Optional[str]
    team: Optional[str]
    version: Optional[str]
    uid: Optional[str]
    table_name: str


class ListResponse(BaseModel):
    records: Optional[List[Dict[str, Any]]]


class AddRecordRequest(BaseModel):
    record: Dict[str, Any]
    table_name: str


class AddRecordResponse(BaseModel):
    registered: bool


class UpdateRecordRequest(BaseModel):
    record: Dict[str, Any]
    table_name: str


class UpdateRecordResponse(BaseModel):
    updated: bool


class QueryRecordRequest(BaseModel):
    name: Optional[str]
    team: Optional[str]
    version: Optional[str]
    uid: Optional[str]
    table_name: str


class QueryRecordResponse(BaseModel):
    record: Dict[str, Any]


@dataclass
class DownloadModelRequest:
    name: Optional[str] = None
    version: Optional[str] = None
    team: Optional[str] = None
    uid: Optional[str] = None
