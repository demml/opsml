from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from opsml.registry.sql.registry_base import VersionType
from opsml.registry.cards.types import METRICS


class StorageUri(BaseModel):
    storage_uri: str


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
    version_type: VersionType
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
    max_date: Optional[str]
    limit: Optional[int]
    table_name: str


class ListResponse(BaseModel):
    cards: Optional[List[Dict[str, Any]]]


class AddCardRequest(BaseModel):
    card: Dict[str, Any]
    table_name: str


class AddCardResponse(BaseModel):
    registered: bool


class UpdateCardRequest(BaseModel):
    card: Dict[str, Any]
    table_name: str


class UpdateCardResponse(BaseModel):
    updated: bool


class QuerycardRequest(BaseModel):
    name: Optional[str]
    team: Optional[str]
    version: Optional[str]
    uid: Optional[str]
    table_name: str


class QuerycardResponse(BaseModel):
    card: Dict[str, Any]


class DownloadModelRequest(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    team: Optional[str] = None
    uid: Optional[str] = None


class DownloadFileRequest(BaseModel):
    read_path: Optional[str] = None


class ListFileRequest(BaseModel):
    read_path: Optional[str] = None


class ListFileResponse(BaseModel):
    files: List[str]


class MetricRequest(BaseModel):
    name: Optional[str]
    team: Optional[str]
    version: Optional[str]
    uid: Optional[str]


class MetricResponse(BaseModel):
    metrics: METRICS
