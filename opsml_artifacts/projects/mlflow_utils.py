# pylint: disable=invalid-envvar-value
import os
from typing import Optional, cast

from mlflow.tracking import MlflowClient

from opsml_artifacts import CardRegistry
from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.helpers.types import OpsmlAuth
from opsml_artifacts.projects.types import CardRegistries
from opsml_artifacts.registry.storage.storage_system import (
    MlflowStorageClient,
    StorageClientGetter,
    StorageClientType,
    StorageSystem,
)
from opsml_artifacts.registry.storage.types import StorageClientSettings


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


def get_card_registries(storage_client: StorageClientType):

    """Gets CardRegistries to associate with MlFlow experiment"""
    registries = CardRegistries(
        datacard=CardRegistry(registry_name="data"),
        modelcard=CardRegistry(registry_name="model"),
        experimentcard=CardRegistry(registry_name="experiment"),
    )

    # double check
    if not isinstance(registries.datacard.registry.storage_client, MlflowStorageClient):
        registries.set_storage_client(storage_client=storage_client)

    return registries


def get_project_id(self, project_id: str, mlflow_client: MlflowClient) -> str:
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
