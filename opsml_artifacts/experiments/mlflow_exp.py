import os
from typing import Optional, Dict, Union
from mlflow.entities import RunStatus, Run
from mlflow.tracking import MlflowClient
from opsml_artifacts import CardRegistry
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.sql.registry import CardTypes
from opsml_artifacts.registry.storage.storage_system import MlFlowStorageClient
from opsml_artifacts.experiments.mlflow_helpers import CardRegistries, mlflow_storage_client

# Notes during development
# assume you are using mlflow url with a proxy client for artifacts
#  Add ApiRegistry with call paths to update opsml
# Needs: Absolute path for mlflow artifacts (base bucket path)

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

        # set the registries
        self.registries = CardRegistries(
            datacard=CardRegistry(registry_name="data"),
            modelcard=CardRegistry(registry_name="model"),
            experimentcard=CardRegistry(registry_name="experiment"),
        )

        self._storage_client = self._get_storage_client()

    def _get_storage_client(self) -> MlFlowStorageClient:
        """Updates mlflow storage client with current mlflow client"""
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

        if bool(self._active_run):
            return self._active_run.info.run_id

        raise ValueError("Active run has not been set")

    @property
    def _extra_registration_kwargs(self) -> Dict[str, Union[MlflowClient, str]]:
        """Creates mlflow-specific kwargs to pass to registry when
        registering an Artifact Card

        Returns:
            Dictionary of kwargs
        """

        return {
            "mlflow_client": self._mlflow_client,
            "run_id": self.run_id,
        }

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
        self._mlflow_client.set_terminated(run_id=self.run_id)

        # Remove run id
        self._storage_client.set_run_id(run_id=None)
        logger.info("experiment complete")

    def register_card(self, card: CardTypes, version_type: str = "minor"):
        """Register a given artifact card

        Args:
            card (CardTypes): DataCard or ModelCard
            version_type (str): Version type for increment. Options are "major", "minor" and
            "patch". Defaults to "minor"
        """

        card_type = card.__class__.__name__.lower()
        registry: CardRegistry = getattr(self.registries, card_type)
        registry.register_card(card=card, version_type=version_type)
