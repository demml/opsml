import os
from dataclasses import dataclass
from typing import Optional, cast

from mlflow.entities import Run, RunStatus
from mlflow.tracking import MlflowClient
from pydantic import BaseModel

from opsml_artifacts import CardRegistry
from opsml_artifacts.experiments.types import (
    ActiveRun,
    CardInfo,
    Experiment,
    ExperimentInfo,
)
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.registry.cards.cards import Card
from opsml_artifacts.registry.storage.storage_system import (
    MlFlowStorageClient,
    StorageClientGetter,
    StorageClientType,
    StorageSystem,
)
from opsml_artifacts.registry.storage.types import StorageClientSettings

# Notes during development
# assume you are using mlflow url with a proxy client for artifacts
# Needs: Absolute path for mlflow artifacts (base bucket path)
# Use the api paths to swap mlflow_root with mlflow_destination when registering card?

logger = ArtifactLogger.get_logger(__name__)


@dataclass
class MlFlowExperimentInfo(ExperimentInfo):
    tracking_uri: Optional[str] = None


class CardRegistries(BaseModel):
    datacard: CardRegistry
    modelcard: CardRegistry
    experimentcard: CardRegistry

    class Config:
        arbitrary_types_allowed = True
        allow_mutation = True

    def set_storage_client(self, storage_client: StorageClientType):
        self.datacard.registry.storage_client = storage_client
        self.modelcard.registry.storage_client = storage_client
        self.experimentcard.registry.storage_client = storage_client


def get_mlflow_storage_client() -> MlFlowStorageClient:
    """Sets MlFlowStorageClient is it is not currently set in settings"""

    if not isinstance(settings.storage_client, MlFlowStorageClient):
        return cast(
            MlFlowStorageClient,
            StorageClientGetter.get_storage_client(
                storage_settings=StorageClientSettings(storage_type=StorageSystem.MLFLOW.value),
            ),
        )
    return cast(MlFlowStorageClient, settings.storage_client)


mlflow_storage_client = get_mlflow_storage_client()


class MlFlowExperiment(Experiment):
    def __init__(self, info: MlFlowExperimentInfo):
        """Instantiates an MlFlow experiment that can log artifacts
        and cards to the Opsml Registry

        Args:
            info: experiment information
        """

        # user supplied
        self.team_name = info.team
        self.user_email = info.user_email
        self.project_name = info.name.lower()

        # tracking attr
        self._active_run: Optional[Run] = None
        self._project_id: Optional[str] = None

        self._mlflow_client = MlflowClient(
            tracking_uri=info.tracking_uri or os.environ.get("OPSML_TRACKING_URI"),
        )

        self._storage_client = self._get_storage_client()
        self.registries = self._get_card_registries()

    def _get_card_registries(self):

        """Gets CardRegistries to associate with MlFlow experiment"""
        registries = CardRegistries(
            datacard=CardRegistry(registry_name="data"),
            modelcard=CardRegistry(registry_name="model"),
            experimentcard=CardRegistry(registry_name="experiment"),
        )

        if not isinstance(registries.datacard.registry.storage_client, MlFlowStorageClient):
            registries.set_storage_client(storage_client=self._storage_client)

        return registries

    def _get_storage_client(self) -> MlFlowStorageClient:
        """Gets the MlFlowStorageClient and sets the current client"""

        mlflow_storage_client.mlflow_client = self._mlflow_client
        return mlflow_storage_client

    @property
    def artifact_save_path(self) -> str:
        """Returns the path where artifacts are saved."""
        self._active_run = cast(ActiveRun, self._active_run)
        return self._active_run.info._artifact_uri  # pylint: disable=protected-access

    @property
    def project_id(self):
        """Returns the mlflow Project id"""
        if bool(self._project_id):
            return self._project_id

        raise ValueError("No project id has been found")

    @property
    def run_id(self) -> str:
        """Run id for mlflow run"""

        if self._active_run is not None:
            return str(self._active_run.info.run_id)

        raise ValueError("Active run has not been set")

    def _get_existing_project_id(self) -> Optional[str]:
        project = self._mlflow_client.get_experiment_by_name(self.project_name)

        if project is None:
            return None

        return project.experiment_id

    def _set_project(self) -> str:
        """Sets the project to use with mlflow. If a project_id associated
        with a project name does not exist it is created

        Returns:
            project_id
        """

        project_id = self._get_existing_project_id()

        if project_id is None:
            project_id = self._mlflow_client.create_experiment(name=self.project_name)

        return project_id

    def _set_run(self) -> Run:

        """Sets the run id for the project. If an existing run_id is passed,
        The tracking client activates the run. If no existing run_id is passed,
        A new run is created.

        Args:
            project_id (str): Project id

        Returns:
            MlFlow Run
        """

        existing_run_id = os.environ.get("OPSML_RUN_ID")
        if bool(existing_run_id):
            self._mlflow_client.update_run(
                run_id=existing_run_id,
                status=RunStatus.RUNNING,
            )
            return self._mlflow_client.get_run(existing_run_id)
        return self._mlflow_client.create_run(experiment_id=self.project_id)

    def __enter__(self):

        self._project_id = self._set_project()
        self._active_run = self._set_run()

        # set storage client run id
        self._storage_client.run_id = self.run_id
        self._storage_client.artifact_path = self.artifact_save_path
        logger.info("starting experiment")

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):

        # set run to terminated
        self._mlflow_client.set_terminated(run_id=self.run_id)

        # Remove run id
        self._storage_client.run_id = None
        logger.info("experiment complete")

    def register_card(self, card: Card, version_type: str = "minor"):
        """Register a given artifact card

        Args:
            card (Card): DataCard or ModelCard
            version_type (str): Version type for increment. Options are "major", "minor" and
            "patch". Defaults to "minor"
        """

        card_type = card.__class__.__name__.lower()
        registry: CardRegistry = getattr(self.registries, card_type)
        registry.register_card(card=card, version_type=version_type)

    def load_card(self, card_type: str, info: CardInfo) -> Card:
        """Returns an artifact card.

        Args:
            card_type:
                datacard or modelcard
            info:
                Card information to retrieve. `uid` takes precedence if it
                exists. If the optional `version` is specified, that version
                will be loaded. If it doesn't exist, the most recent ersion will
                be loaded.
        """
        registry: CardRegistry = getattr(self.registries, f"{card_type.lower()}card")
        return registry.load_card(name=info.name, team=info.team, version=info.version, uid=info.uid)
