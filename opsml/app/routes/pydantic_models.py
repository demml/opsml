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
    version: str
    proxy: bool = False


class VersionRequest(BaseModel):
    name: str
    team: str
    version: Optional[str] = None
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
    uid: Optional[str] = None


class CompareCardRequest(BaseModel):
    name: Optional[str] = None
    team: Optional[str] = None
    versions: Optional[List[str]] = None
    uids: Optional[List[str]] = None


class RegisterModelRequest(BaseModel):
    name: str = Field(
        ...,
        description="Model name (does not include team)",
        example="tlmd-drive-time",
    )
    version: str = Field(
        ...,
        regex="^[0-9]+(.[0-9]+)?(.[0-9]+)?$",
        description="""
                Version of model to register in major[.minor[.patch]] format. Valid
                formats are "1", "1.1", and "1.1.1". If not all components are
                specified, the latest version for the leftmost missing component
                will be registered.

                For example, assume the latest version is 1.2.3 and versions 1.1.1 thru 1.1.100 exist
                    * "1"     = registers 1.2.3 at "1" (the highest minor / patch version is used)
                    * "1.2"   = registers 1.2.3 at "1.2"
                    * "1.1"   = registers 1.1.100 at "1.1"
                    * "1.1.1" = registers 1.1.1 at "1.1.1"
                """,
    )
    onnx: bool = Field(
        True, description="Flag indicating if the onnx or non-onnx model should be registered. Default True."
    )


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
