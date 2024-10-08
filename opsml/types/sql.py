# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum, unique
from typing import Any, Dict, List, Optional, Protocol


@unique
class RegistryTableNames(str, Enum):
    DATA = "OPSML_DATA_REGISTRY"
    MODEL = "OPSML_MODEL_REGISTRY"
    RUN = "OPSML_RUN_REGISTRY"
    PIPELINE = "OPSML_PIPELINE_REGISTRY"
    PROJECT = "OPSML_PROJECT_REGISTRY"
    AUDIT = "OPSML_AUDIT_REGISTRY"
    BASE = "OPSML_BASE_REGISTRY"
    METRICS = "OPSML_RUN_METRICS"
    HARDWARE_METRICS = "OPSML_RUN_HARDWARE_METRICS"
    AUTH = "OPSML_AUTH_REGISTRY"
    PARAMETERS = "OPSML_RUN_PARAMETERS"
    MESSAGE = "OPSML_MESSAGE_REGISTRY"

    @staticmethod
    def from_str(name: str) -> "RegistryTableNames":
        l_name = name.strip().lower()
        if l_name == "data":
            return RegistryTableNames.DATA
        if l_name == "model":
            return RegistryTableNames.MODEL
        if l_name == "run":
            return RegistryTableNames.RUN
        if l_name == "pipeline":
            return RegistryTableNames.PIPELINE
        if l_name == "project":
            return RegistryTableNames.PROJECT
        if l_name == "audit":
            return RegistryTableNames.AUDIT
        if l_name == "metric":
            return RegistryTableNames.METRICS
        if l_name == "parameter":
            return RegistryTableNames.PARAMETERS

        raise NotImplementedError()


class RunCardRegistry(Protocol):
    def insert_parameter(self, parameter: List[Dict[str, Any]]) -> None: ...

    def insert_metric(self, metric: List[Dict[str, Any]]) -> None: ...

    def insert_hw_metrics(self, metrics: List[Dict[str, Any]]) -> None: ...

    def get_hw_metric(self, run_uid: str) -> Optional[List[Dict[str, Any]]]: ...

    def get_metric(
        self,
        run_uid: str,
        name: Optional[List[str]] = None,
        names_only: bool = False,
    ) -> List[Dict[str, Any]]: ...

    def get_parameter(
        self,
        run_uid: str,
        name: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]: ...
