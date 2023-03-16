from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class HealthCheckResult(BaseModel):
    is_alive: bool


class StorageSettingsResponse(BaseModel):
    storage_type: str
    storage_uri: str


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
