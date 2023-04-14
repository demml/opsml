# pylint: disable=invalid-envvar-value
import os
from typing import Optional

from mlflow.tracking import MlflowClient

from opsml_artifacts.helpers.types import OpsmlAuth
from opsml_artifacts.projects.base.types import CardRegistries, RunInfo
from opsml_artifacts.registry import RunCard
from opsml_artifacts.registry.storage.storage_system import StorageClientType


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


# def get_mlflow_storage_client() -> MlflowStorageClient:
#    """Sets MlflowStorageClient is it is not currently set in settings"""
#
#    if not isinstance(settings.storage_client, MlflowStorageClient):
#        return cast(
#            MlflowStorageClient,
#            StorageClientGetter.get_storage_client(
#                storage_settings=StorageClientSettings(storage_type=StorageSystem.MLFLOW.value),
#            ),
#        )
#    return cast(MlflowStorageClient, settings.storage_client)
#


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


# class MlflowMgrClient(metaclass=Singleton):
#    def __init__(self, tracking_uri: str):
#        self.tracking_client = MlflowClient(tracking_uri=tracking_uri)
#        self.storage_client = get_mlflow_storage_client()
#        self.storage_client.mlflow_client = self.tracking_client
#
#
# def get_mlflow_client_defaults(tracking_uri: Optional[str]) -> MlflowMgrClient:
#    """
#    Gets and sets MlFlow-related authentication. MlflowProject needs both an
#    mlflow_client for interacting with mlflow and an mlflowstorageclient that follows opsml
#    conventions for storing cards/artifacts. Future plans are to get away from
#    using mlflowstorageclient and instead use one of the default file systems like GcsFileSystem.
#
#    This function is used to set both clients and ensure only one is ever created.
#
#    Args:
#        tracking_uri (str): MlFLow tracking uri
#
#    Returns:
#        MlFlow tracking client
#    """
#
#    set_env_vars(tracking_uri=str(tracking_uri))
#    return MlflowMgrClient(tracking_uri=str(tracking_uri))
#
