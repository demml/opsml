# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Union

import pandas as pd
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict

from opsml.helpers.request_helpers import ApiClient

FilePath = Union[List[str], str]


class ArtifactStorageType(str, Enum):
    PANDAS_DATAFRAME = "PandasDataFrame"
    POLARS_DATAFRAME = "PolarsDataFrame"
    ARROW_TABLE = "Table"
    NDARRAY = "ndarray"
    TF_MODEL = "keras"
    PYTORCH = "pytorch"
    JSON = "json"
    BOOSTER = "booster"
    ONNX = "onnx"
    IMAGE_DATASET = "ImageDataset"


ARTIFACT_TYPES = list(ArtifactStorageType)


class StorageClientSettings(BaseModel):
    storage_type: str = "local"
    storage_uri: str = os.getcwd()


class GcsStorageClientSettings(StorageClientSettings):
    storage_type: str = "gcs"
    credentials: Optional[Any] = None
    gcp_project: Optional[str] = None


class S3StorageClientSettings(StorageClientSettings):
    storage_type: str = "s3"


class ApiStorageClientSettings(StorageClientSettings):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=False)

    client: Optional[ApiClient] = None

    @property
    def api_client(self) -> ApiClient:
        if self.client is not None:
            return self.client
        raise ValueError("ApiClient has not been set")


StorageSettings = Union[
    StorageClientSettings,
    GcsStorageClientSettings,
    ApiStorageClientSettings,
    S3StorageClientSettings,
]


class ArtifactStorageSpecs(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=False)

    save_path: str
    filename: Optional[str] = None


class MlFlowClientProto(Protocol):
    def log_artifact(self, run_id: str, local_path: str, artifact_path: str):
        "log artifact"

    def _record_logged_model(self, run_id: str, mlflow_model: Any):
        "record logged model"


class MlflowModelFlavor(Protocol):
    def save_model(
        self,
        path: str,
        mlflow_model: Any,
        signature: Any,
        input_example: Union[pd.DataFrame, NDArray, Dict[str, NDArray]],
        **kwargs,
    ):
        "Save model flavor"


class MlflowModel(Protocol):
    def get_model_info(self):
        ...


class MlflowModelInfo(Protocol):
    @property
    def artifact_path(self):
        ...

    @property
    def flavors(self):
        ...

    @property
    def model_uri(self):
        ...

    @property
    def model_uuid(self):
        ...

    @property
    def run_id(self):
        ...

    @property
    def saved_input_example_info(self):
        ...

    @property
    def signature_dict(self):
        ...

    @property
    def signature(self):  # -> Optional[ModelSignature]
        ...

    @property
    def utc_time_created(self):
        ...

    @property
    def mlflow_version(self):
        ...

    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        ...


@dataclass
class MlflowInfo:
    local_path: str
    artifact_path: str
    filename: str
    model: Optional[Any] = None
    model_type: Optional[str] = None
