import os
from typing import Optional

from mlflow.entities import Run, RunStatus
from mlflow.tracking import MlflowClient

from opsml_artifacts import CardRegistry
from opsml_artifacts.experiments.mlflow_helpers import (
    CardRegistries,
    mlflow_storage_client,
)
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.sql.registry import CardType
from opsml_artifacts.registry.storage.storage_system import MlFlowStorageClient

# Notes during development
# assume you are using mlflow url with a proxy client for artifacts
# Needs: Absolute path for mlflow artifacts (base bucket path)
# Use the api paths to swap mlflow_root with mlflow_destination when registering card?

logger = ArtifactLogger.get_logger(__name__)


class MlFlowExperiment:
    def __init__(
        self,
        project_name: str,
        team_name: str,
        user_email: str,
        tracking_uri: Optional[str] = None,
    ):

        """Instantiates an MlFlow experiment that can log artifacts
        and cards to the Opsml Registry

        Args:
            project_name (str): Name of current project
            team_name (str): Team name
            user_email (str): Email of user performing experiment
            tracking_uri (str): Optional uri of opsml registry
        """

        # user supplied
        self.team_name = team_name
        self.user_email = user_email
        self.project_name = project_name.lower()

        # tracking attr
        self._active_run: Optional[Run] = None
        self._project_id: Optional[str] = None

        self._mlflow_client = MlflowClient(
            tracking_uri=tracking_uri or os.environ.get("OPSML_TRACKING_URI"),
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

        mlflow_storage_client.set_mlflow_client(mlflow_client=self._mlflow_client)
        return mlflow_storage_client

    @property
    def artifact_save_path(self) -> str:
        """Save path to use when registering Artifact Cards

        Returns:
            artifact save path
        """
        return f"{self.project_id}/{self.run_id}/artifacts"

    @property
    def project_id(self):
        """Project id associated with project name in mlflow

        Returns:
            project id string
        """
        if bool(self._project_id):
            return self._project_id

        raise ValueError("No project id has been found")

    @property
    def run_id(self) -> str:
        """Run id for mlflow run"""

        if self._active_run is not None:
            return str(self._active_run.info.run_id)

        raise ValueError("Active run has not been set")

    def _set_project(self) -> str:
        """Sets the project to use with mlflow. If a project_id associated
        with a project name does not exist it is created

        Returns:
            project_id
        """
        project_id = self._mlflow_client.get_experiment_by_name(self.project_name)

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
        self._storage_client.set_run_id(run_id=self.run_id)
        logger.info("starting experiment")

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):

        # set run to terminated
        self._mlflow_client.set_terminated(run_id=self.run_id)

        # Remove run id
        self._storage_client.set_run_id(run_id=None)
        logger.info("experiment complete")

    def register_card(self, card: CardType, version_type: str = "minor"):
        """Register a given artifact card

        Args:
            card (CardType): DataCard or ModelCard
            version_type (str): Version type for increment. Options are "major", "minor" and
            "patch". Defaults to "minor"
        """

        card_type = card.__class__.__name__.lower()
        registry: CardRegistry = getattr(self.registries, card_type)
        registry.register_card(
            card=card,
            version_type=version_type,
            save_path=self.artifact_save_path,
        )

    def load_card(
        self,
        card_type: str,
        name: Optional[str] = None,
        team: Optional[str] = None,
        uid: Optional[str] = None,
        version: Optional[str] = None,
    ) -> CardType:

        """Loads a specific card

        Args:
            card_type (str): datacard or modelcard
            name (str): Optional Card name
            team (str): Optional team associated with card
            version (int): Optional version number of existing data. If not specified,
            the most recent version will be used
            uid (str): Unique identifier for the card. If present, the uid takes precedence.

        Returns
            ArtifactCard
        """
        registry: CardRegistry = getattr(self.registries, f"{card_type.lower()}card")
        return registry.load_card(name=name, team=team, version=version, uid=uid)
