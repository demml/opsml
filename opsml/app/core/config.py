# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

import os

BASE_LOCAL_SQL = f"sqlite:///{os.path.expanduser('~')}/opsml_database.db"
TRACKING_URI = os.environ.get("OPSML_TRACKING_URI", BASE_LOCAL_SQL)
STORAGE_URI = os.environ.get("OPSML_STORAGE_URI", "./mlruns")


class MlFlowConfig:
    MLFLOW_SERVER_ARTIFACT_DESTINATION = os.getenv("_MLFLOW_SERVER_ARTIFACT_DESTINATION", STORAGE_URI)
    MLFLOW_SERVER_ARTIFACT_ROOT = os.getenv("_MLFLOW_SERVER_ARTIFACT_ROOT", "mlflow-artifacts:/")
    MLFLOW_SERVER_FILE_STORE = os.getenv("_MLFLOW_SERVER_FILE_STORE", TRACKING_URI)
    MLFLOW_SERVER_SERVE_ARTIFACTS = bool(os.getenv("_MLFLOW_SERVER_SERVE_ARTIFACTS", "true"))

    def __init__(self) -> None:
        self._set_mlflow_vars()

    def _set_mlflow_vars(self) -> None:
        """Ensures mlflow environment variables exist"""

        os.environ["_MLFLOW_SERVER_ARTIFACT_DESTINATION"] = self.MLFLOW_SERVER_ARTIFACT_DESTINATION
        os.environ["_MLFLOW_SERVER_ARTIFACT_ROOT"] = self.MLFLOW_SERVER_ARTIFACT_ROOT
        os.environ["_MLFLOW_SERVER_FILE_STORE"] = self.MLFLOW_SERVER_FILE_STORE
        os.environ["_MLFLOW_SERVER_SERVE_ARTIFACTS"] = str(self.MLFLOW_SERVER_SERVE_ARTIFACTS).lower()


class OpsmlConfig:
    APP_NAME = "OPSML-API"
    APP_ENV = os.environ.get("APP_ENV", "development")
    STORAGE_URI = STORAGE_URI
    TRACKING_URI = TRACKING_URI
    PROD_TOKEN = os.environ.get("OPSML_PROD_TOKEN", "staging")

    def __init__(self) -> None:
        self._proxy_root = os.environ.get("PROXY_ROOT")
        self._is_proxy = False

    @property
    def proxy_root(self) -> Optional[str]:
        return self._proxy_root

    @proxy_root.setter
    def proxy_root(self, root: str) -> None:
        self._proxy_root = root

    @property
    def is_proxy(self) -> bool:
        return self._is_proxy

    @is_proxy.setter
    def is_proxy(self, proxy: bool) -> None:
        self._is_proxy = proxy


config = OpsmlConfig()
