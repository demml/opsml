# pylint: disable=invalid-envvar-value
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from typing import Optional

from mlflow.tracking import MlflowClient

from opsml.helpers.types import OpsmlAuth
from opsml.projects.base._active_run import RunInfo
from opsml.registry import CardRegistries, RunCard
from opsml.registry.storage.storage_system import StorageClientType


class MlflowRunInfo(RunInfo):
    def __init__(
        self,
        mlflow_client: MlflowClient,
        storage_client: StorageClientType,
        registries: CardRegistries,
        runcard: RunCard,
        run_id: str,
        base_artifact_uri: str,
        run_name: Optional[str] = None,
    ):
        super().__init__(
            storage_client=storage_client,
            registries=registries,
            runcard=runcard,
            run_id=run_id,
            run_name=run_name,
        )

        self.mlflow_client = mlflow_client
        self.base_artifact_path = base_artifact_uri


def set_env_vars(tracking_uri: str):
    """
    Sets mlflow env vars for current python runtime
    """

    # set global tracking uri: When logging artifacts, mlflow will call the env var
    os.environ["MLFLOW_TRACKING_URI"] = tracking_uri

    # set username and password while running project
    if all(bool(os.getenv(cred)) for cred in OpsmlAuth):
        os.environ["MLFLOW_TRACKING_USERNAME"] = str(os.getenv(OpsmlAuth.USERNAME))
        os.environ["MLFLOW_TRACKING_PASSWORD"] = str(os.getenv(OpsmlAuth.PASSWORD))
