# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator
from opsml.model.challenger import BattleReport
from opsml.registry.cards.types import METRICS
from opsml.registry.sql.base.registry_base import VersionType
from opsml.registry.sql.semver import CardVersion


class StorageUri(BaseModel):
    storage_uri: str


class HealthCheckResult(BaseModel):
    is_alive: bool


class DebugResponse(BaseModel):
    url: str
    storage: str
    app_env: str
    proxy_root: Optional[str] = None
    is_proxy: Optional[bool] = None


class StorageSettingsResponse(BaseModel):
    storage_type: str
    storage_uri: str
    version: str
    proxy: bool = False


class VersionRequest(BaseModel):
    name: str
    team: str
    version: Optional[CardVersion] = None
    version_type: VersionType
    table_name: str
    pre_tag: str = "rc"
    build_tag: str = "build"


class VersionResponse(BaseModel):
    version: str


class UidExistsRequest(BaseModel):
    uid: str
    table_name: str


class UidExistsResponse(BaseModel):
    uid_exists: bool


class ListCardRequest(BaseModel):
    name: Optional[str] = None
    team: Optional[str] = None
    version: Optional[str] = None
    uid: Optional[str] = None
    max_date: Optional[str] = None
    limit: Optional[int] = None
    tags: Optional[Dict[str, str]] = None
    ignore_release_candidates: bool = False
    table_name: str

    @model_validator(mode="before")
    def update_limit(cls, env_vars: Dict[str, Optional[Union[str, int]]]):
        if not any((env_vars.get(key) for key in ["name", "team", "limit"])):
            env_vars["limit"] = 20
        return env_vars


class ListCardResponse(BaseModel):
    cards: Optional[List[Dict[str, Any]]] = None


class AddCardRequest(BaseModel):
    card: Dict[str, Any]
    table_name: str


class AddCardResponse(BaseModel):
    registered: bool


class UpdateCardRequest(BaseModel):
    card: Dict[str, Any]
    table_name: str


class DeleteCardRequest(BaseModel):
    card: Dict[str, Any]
    table_name: str


class UpdateCardResponse(BaseModel):
    updated: bool


class DeleteCardResponse(BaseModel):
    deleted: bool


class QuerycardRequest(BaseModel):
    name: Optional[str] = None
    team: Optional[str] = None
    version: Optional[str] = None
    uid: Optional[str] = None
    table_name: str


class QuerycardResponse(BaseModel):
    card: Dict[str, Any]


class CardRequest(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    uid: Optional[str] = None
    ignore_release_candidate: bool = False


class CompareCardRequest(BaseModel):
    name: Optional[str] = None
    team: Optional[str] = None
    versions: Optional[List[str]] = None
    uids: Optional[List[str]] = None


class RegisterModelRequest(BaseModel):
    name: str = Field(..., description="Model name (does not include team)")
    version: str = Field(
        ...,
        pattern="^[0-9]+(.[0-9]+)?(.[0-9]+)?$",
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


class DeleteFileResponse(BaseModel):
    deleted: bool


class DeleteFileRequest(BaseModel):
    read_path: str


class MetricRequest(BaseModel):
    name: Optional[str] = None
    team: Optional[str] = None
    version: Optional[str] = None
    uid: Optional[str] = None


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
