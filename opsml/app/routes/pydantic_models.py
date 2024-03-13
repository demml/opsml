# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, List, Optional, Union

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field, model_validator

from opsml.cards.audit import AuditSections
from opsml.model.challenger import BattleReport
from opsml.registry.semver import CardVersion, VersionType
from opsml.types import Comment


class Success(BaseModel):
    complete: bool = True


class HealthCheckResult(BaseModel):
    is_alive: bool


class ListRepositoryNameInfo(BaseModel):
    repositories: Optional[List[str]] = None
    selected_repository: Optional[str] = None
    names: Optional[List[str]] = None


class DebugResponse(BaseModel):
    url: str
    storage: str
    app_env: str


class StorageSettingsResponse(BaseModel):
    storage_type: str
    storage_uri: str
    version: str


class VersionRequest(BaseModel):
    name: str
    repository: str
    version: Optional[CardVersion] = None
    version_type: VersionType
    registry_type: Optional[str] = None
    table_name: Optional[str] = None
    pre_tag: str = "rc"
    build_tag: str = "build"


class VersionResponse(BaseModel):
    version: str


class UidExistsRequest(BaseModel):
    uid: str
    registry_type: Optional[str] = None
    table_name: Optional[str] = None


class UidExistsResponse(BaseModel):
    uid_exists: bool


class DownloadFileRequest(BaseModel):
    read_path: Optional[str] = None


class PutFileRequest(BaseModel):
    write_path: str


class ListCardRequest(BaseModel):
    name: Optional[str] = None
    repository: Optional[str] = None
    version: Optional[str] = None
    uid: Optional[str] = None
    max_date: Optional[str] = None
    limit: Optional[int] = None
    tags: Optional[Dict[str, str]] = None
    ignore_release_candidates: bool = False
    project_id: Optional[str] = None
    registry_type: Optional[str] = None
    table_name: Optional[str] = None
    query_terms: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def update_limit(cls, env_vars: Dict[str, Optional[Union[str, int]]]) -> Dict[str, Optional[Union[str, int]]]:
        if not any((env_vars.get(key) for key in ["name", "repository", "limit"])):
            env_vars["limit"] = 20
        return env_vars


class ListCardResponse(BaseModel):
    cards: Optional[List[Dict[str, Any]]] = None


class AddCardRequest(BaseModel):
    card: Dict[str, Any]
    registry_type: Optional[str] = None
    table_name: Optional[str] = None


class AddCardResponse(BaseModel):
    registered: bool


class UpdateCardRequest(BaseModel):
    card: Dict[str, Any]
    registry_type: Optional[str] = None
    table_name: Optional[str] = None


class DeleteCardRequest(BaseModel):
    card: Dict[str, Any]
    registry_type: Optional[str] = None
    table_name: Optional[str] = None


class UpdateCardResponse(BaseModel):
    updated: bool


class DeleteCardResponse(BaseModel):
    deleted: bool


class QuerycardRequest(BaseModel):
    name: Optional[str] = None
    repository: Optional[str] = None
    version: Optional[str] = None
    uid: Optional[str] = None
    registry_type: Optional[str] = None
    table_name: Optional[str] = None


class QuerycardResponse(BaseModel):
    card: Dict[str, Any]


class CardRequest(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    repository: Optional[str] = None
    uid: Optional[str] = None
    ignore_release_candidate: bool = False


class CompareCardRequest(BaseModel):
    name: Optional[str] = None
    repository: Optional[str] = None
    versions: Optional[List[str]] = None
    uids: Optional[List[str]] = None


class RegisterModelRequest(BaseModel):
    name: str = Field(..., description="Model name (does not include repository)")
    repository: str = Field(..., description="Repository name")
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
    ignore_release_candidate: bool = Field(True, description="Flag indicating if release candidates should be ignored.")


class RepositoriesResponse(BaseModel):
    repositories: List[str] = []


class TableNameResponse(BaseModel):
    table_name: str


class NamesResponse(BaseModel):
    names: List[str] = []


class ListFileRequest(BaseModel):
    read_path: str


class ListFileResponse(BaseModel):
    files: List[str]


class DeleteFileResponse(BaseModel):
    deleted: bool


class FileExistsResponse(BaseModel):
    exists: bool


class DeleteFileRequest(BaseModel):
    read_path: str


class Metric(BaseModel):
    run_uid: str
    name: str
    value: Optional[float] = None
    step: Optional[int] = None
    timestamp: Optional[int] = None


class Metrics(BaseModel):
    metric: Union[Optional[List[Metric]], Optional[List[str]]]


class GetMetricRequest(BaseModel):
    run_uid: str
    name: Optional[List[str]] = None
    names_only: bool = False


class CompareMetricRequest(BaseModel):
    metric_name: List[str]
    lower_is_better: Union[bool, List[bool]]
    challenger_uid: str
    champion_uid: List[str]


class CompareMetricResponse(BaseModel):
    challenger_name: str
    challenger_version: str
    report: Dict[str, List[BattleReport]]


def form_body(cls: Any) -> Any:
    args = []
    params = cls.__signature__.parameters
    for param in params.values():
        if param.name == "audit_file":
            arg = param.replace(default=File(None))
        elif param.default is not None:
            arg = param.replace(default=Form(...))
        else:
            arg = param.replace(default=Form(None))
        args.append(arg)

    cls.__signature__ = cls.__signature__.replace(parameters=args)
    return cls


@form_body
class CommentSaveRequest(BaseModel):
    uid: str
    name: str
    contact: str
    repository: str
    selected_model_name: str
    selected_model_repository: str
    selected_model_version: str
    selected_model_contact: str
    comment_name: str
    comment_text: str


@form_body
class AuditFormRequest(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    repository: Optional[str] = None
    uid: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    selected_model_name: str
    selected_model_repository: str
    selected_model_version: str
    selected_model_contact: str
    audit_file: Optional[UploadFile] = None
    comments: Optional[str] = None
    business_understanding_1: Optional[str] = None
    business_understanding_2: Optional[str] = None
    business_understanding_3: Optional[str] = None
    business_understanding_4: Optional[str] = None
    business_understanding_5: Optional[str] = None
    business_understanding_6: Optional[str] = None
    business_understanding_7: Optional[str] = None
    business_understanding_8: Optional[str] = None
    business_understanding_9: Optional[str] = None
    business_understanding_10: Optional[str] = None
    data_understanding_1: Optional[str] = None
    data_understanding_2: Optional[str] = None
    data_understanding_3: Optional[str] = None
    data_understanding_4: Optional[str] = None
    data_understanding_5: Optional[str] = None
    data_understanding_6: Optional[str] = None
    data_understanding_7: Optional[str] = None
    data_understanding_8: Optional[str] = None
    data_understanding_9: Optional[str] = None
    data_preparation_1: Optional[str] = None
    data_preparation_2: Optional[str] = None
    data_preparation_3: Optional[str] = None
    data_preparation_4: Optional[str] = None
    data_preparation_5: Optional[str] = None
    data_preparation_6: Optional[str] = None
    data_preparation_7: Optional[str] = None
    data_preparation_8: Optional[str] = None
    data_preparation_9: Optional[str] = None
    data_preparation_10: Optional[str] = None
    modeling_1: Optional[str] = None
    modeling_2: Optional[str] = None
    modeling_3: Optional[str] = None
    modeling_4: Optional[str] = None
    modeling_5: Optional[str] = None
    modeling_6: Optional[str] = None
    modeling_7: Optional[str] = None
    modeling_8: Optional[str] = None
    modeling_9: Optional[str] = None
    modeling_10: Optional[str] = None
    modeling_11: Optional[str] = None
    modeling_12: Optional[str] = None
    evaluation_1: Optional[str] = None
    evaluation_2: Optional[str] = None
    evaluation_3: Optional[str] = None
    evaluation_4: Optional[str] = None
    evaluation_5: Optional[str] = None
    deployment_ops_1: Optional[str] = None
    deployment_ops_2: Optional[str] = None
    deployment_ops_3: Optional[str] = None
    deployment_ops_4: Optional[str] = None
    deployment_ops_5: Optional[str] = None
    deployment_ops_6: Optional[str] = None
    deployment_ops_7: Optional[str] = None
    deployment_ops_8: Optional[str] = None
    deployment_ops_9: Optional[str] = None
    deployment_ops_10: Optional[str] = None
    deployment_ops_11: Optional[str] = None
    deployment_ops_12: Optional[str] = None
    deployment_ops_13: Optional[str] = None
    deployment_ops_14: Optional[str] = None
    deployment_ops_15: Optional[str] = None
    deployment_ops_16: Optional[str] = None
    deployment_ops_17: Optional[str] = None
    deployment_ops_18: Optional[str] = None
    deployment_ops_19: Optional[str] = None
    deployment_ops_20: Optional[str] = None
    deployment_ops_21: Optional[str] = None
    deployment_ops_22: Optional[str] = None
    misc_1: Optional[str] = None
    misc_2: Optional[str] = None
    misc_3: Optional[str] = None
    misc_4: Optional[str] = None
    misc_5: Optional[str] = None
    misc_6: Optional[str] = None
    misc_7: Optional[str] = None
    misc_8: Optional[str] = None
    misc_9: Optional[str] = None
    misc_10: Optional[str] = None


class AuditReport(BaseModel):
    name: Optional[str] = None
    repository: Optional[str] = None
    contact: Optional[str] = None
    version: Optional[str] = None
    uid: Optional[str] = None
    status: Optional[bool] = False
    audit: Optional[Dict[str, Any]] = AuditSections().model_dump()  # type: ignore
    timestamp: Optional[str] = None
    comments: List[Optional[Comment]] = []


class ProjectIdResponse(BaseModel):
    project_id: int


# TODO: remove these once everyone is migrated to v2.2.0
class MetricRequest(BaseModel):
    name: Optional[str] = None
    repository: Optional[str] = None
    version: Optional[str] = None
    uid: Optional[str] = None


class MetricResponse(BaseModel):
    metrics: Metrics
