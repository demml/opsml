from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from opsml.model.challenger import BattleReport
from opsml.registry.cards.types import METRICS
from opsml.registry.sql.registry_base import VersionType


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


class ListCardRequest(BaseModel):
    name: Optional[str]
    team: Optional[str]
    version: Optional[str]
    uid: Optional[str]
    max_date: Optional[str]
    limit: Optional[int]
    tags: Optional[Dict[str, str]]
    table_name: str


class ListCardResponse(BaseModel):
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


class CardRequest(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    team: Optional[str] = None
    uid: Optional[str] = None


class CompareCardRequest(BaseModel):
    name: Optional[str] = None
    team: Optional[str] = None
    versions: Optional[List[str]] = None
    uids: Optional[List[str]] = None


class RegisterModelRequest(BaseModel):
    name: str
    version: str = Field(..., regex="^[0-9]+(.[0-9]+)?(.[0-9]+)?$")
    team: str
    uid: Optional[str]
    onnx: bool = True


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


class CompareMetricRequest(BaseModel):
    metric_name: List[str]
    lower_is_better: Union[bool, List[bool]]
    challenger_uid: str
    champion_uid: List[str]


class CompareMetricResponse(BaseModel):
    challenger_name: str
    challenger_version: str
    report: Dict[str, List[BattleReport]]
