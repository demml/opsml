# pylint: disable=invalid-envvar-value
import os
from dataclasses import dataclass
from typing import Optional, cast

from mlflow.tracking import MlflowClient

from opsml_artifacts import CardRegistry
from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.helpers.types import OpsmlAuth
from opsml_artifacts.projects.base.types import CardRegistries, RunInfo, MlflowProjectInfo
from opsml_artifacts.registry.storage.storage_system import (
    MlflowStorageClient,
    StorageClientGetter,
    StorageClientType,
    StorageSystem,
)
from opsml_artifacts.registry.storage.types import StorageClientSettings


@dataclass
class MlflowRunInfo:
    storage_client: MlflowStorageClient
    mlflow_client: MlflowClient
    project_info: MlflowProjectInfo
    registries: CardRegistries
    run_name: Optional[str] = None
    run_id: Optional[str] = None


def get_mlflow_storage_client() -> MlflowStorageClient:
    """Sets MlflowStorageClient is it is not currently set in settings"""

    if not isinstance(settings.storage_client, MlflowStorageClient):
        return cast(
            MlflowStorageClient,
            StorageClientGetter.get_storage_client(
                storage_settings=StorageClientSettings(storage_type=StorageSystem.MLFLOW.value),
            ),
        )
    return cast(MlflowStorageClient, settings.storage_client)


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


mlflow_storage_client = get_mlflow_storage_client()


def get_mlflow_client(tracking_uri: Optional[str]) -> MlflowClient:
    """Gets and sets MlFlow-related authentication

    Args:
        tracking_uri (str): MlFLow tracking uri

    Returns:
        MlFlow tracking client
    """

    set_env_vars(tracking_uri=str(tracking_uri))
    mlflow_client = MlflowClient(tracking_uri=tracking_uri)

    return mlflow_client


def get_project_id(project_id: str, mlflow_client: MlflowClient) -> str:
    """
    Finds the project_id from mlflow for the given project. If an
    existing proejct does not exist, a new one is created.

    Args:
        project_id:
            Project identifier
        mlflow_client:
            MlflowClient instance

    Returns:
        The underlying mlflow project_id
    """
    # REMINDER: We treat mlflow "experiments" as projects
    project = mlflow_client.get_experiment_by_name(name=project_id)
    if project is None:
        return mlflow_client.create_experiment(name=project_id)
    return project.experiment_id
