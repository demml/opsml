import os
from typing import Optional, cast

from mlflow.entities import Run, RunStatus
from mlflow.entities.run_data import RunData
from mlflow.entities.run_info import RunInfo
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient
from pydantic import BaseModel, Field

from opsml_artifacts import CardRegistry
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.projects.types import Project, ProjectInfo
from opsml_artifacts.registry.cards import cards
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


class MlFlowProjectInfo(ProjectInfo):
    """An mlflow project identifier.

    Identifies a project with an mlflow backend. By default, projects in mlflow
    are "experiments". Each project is named after the team and project name
    with the conention "team:name".

    The following project shows up as an "experiment" in mlflow with the name:

    "devops-ml:iris".

    Args:
        name:
            The project name. Must be unique per team.
        team:
            The team owning the project.
        user_email:
            Optional user email to associate with the project
        run_id:
            The run to open the project at. By default, the run will be opened
            in "read only" mode by the project. To open the run for read /
            write, open it within a context manager.


    """

    run_id: Optional[str] = Field(
        None,
        description="An existing mlflow run_id to use. If None, a new run is created when the project is activated",
    )
    tracking_uri: Optional[str] = Field(
        None,
        description="The mlflow tracking URI. Defaults to OPSML_TRACKING_URI",
    )

    def mlflow_experiment_name(self) -> str:
        return f"{self.team}:{self.name}"


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


class MlFlowProject(Project):
    def __init__(self, info: MlFlowProjectInfo):
        """Instantiates an mlflow project which log cards, metrics and params to
            the opsml registry and mlflow via a "run" object.

            If info.run_id is set, that run_id will be loaded as read only. In read
            only mode, you can retrieve cards, metrics, and params, however you
            cannot write new data. If you want to write new data to the run, you
            have to make it active via a context manager.

            Example:

                project: MlFlowProject = get_project(
                    MlFlowProjectInfo(
                        name="test-project",
                        team="devops-ml",
                        # If run_id is onitted, a new run is created.
                        run_id="123ab123kaj8u8naskdfh813",
                    )
                )
                # the project is in "read only" mode. all read operations will work
                for k, v in project.params:
                    logger.info("%s = %s", k, v)

                with mlflow_exp as project:
                    # Now that the project context is entered, it's in read/write mode
                    # You can write cards, params, and metrics to the project.
                    project.log_param(key="my_param", value="12.34")
        )

            Args:
                info: experiment information. if a run_id is given, that run is set
                as the project's current run.
        """

        # user supplied
        self.name = info.name.lower()
        self.team_name = info.team
        self.user_email = info.user_email
        self._experiment_name = info.mlflow_experiment_name()

        # tracking attr
        self._run_id: Optional[str] = None
        self._active_run: Optional[Run] = None

        self._mlflow_client = MlflowClient(
            tracking_uri=info.tracking_uri or os.environ.get("OPSML_TRACKING_URI"),
        )

        self._storage_client = self._get_storage_client()
        self.registries = self._get_card_registries()

        self._project_id = self._get_project_id(self._experiment_name)
        if info.run_id is not None:
            self._verify_run_id(info.run_id)
            self._run_id = info.run_id

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
        self._verify_active()
        info: RunInfo = cast(Run, self._active_run).info
        return info.artifact_uri

    @property
    def run_id(self) -> Optional[str]:
        """Run id for mlflow run"""
        return self._run_id

    @property
    def project_id(self):
        """Returns the mlflow Project id"""
        return self._project_id

    def _get_project_id(self, name: str) -> str:
        """Finds the project_id from mlflow for the given name. If an existing
        project does not exist, a new one is created.

        Returns:
            the underlying mlflow experiment_id (which is our project_id)
        """
        project = self._mlflow_client.get_experiment_by_name(name=name)
        if project is None:
            return self._mlflow_client.create_experiment(name=name)
        return project.experiment_id

    def _verify_run_id(self, run_id: str) -> None:
        """Verifies the run exists for the given project."""
        try:
            self._mlflow_client.get_run(run_id)
        except MlflowException as exc:
            raise ValueError("Invalid run_id") from exc

    def __enter__(self):
        if self._active_run is not None:
            raise ValueError("Could not start run. Another run is current active")

        if self.run_id is not None:
            self._mlflow_client.update_run(
                run_id=self.run_id,
                status=RunStatus.to_string(RunStatus.RUNNING),
            )
            self._active_run = self._mlflow_client.get_run(self._run_id)
        else:
            self._active_run = self._mlflow_client.create_run(experiment_id=self.project_id)

        info = cast(RunInfo, self._active_run.info)
        self._run_id = info.run_id
        # set storage client run id
        self._storage_client.run_id = self._run_id
        self._storage_client.artifact_path = self.artifact_save_path
        logger.info("starting run: %s", self._run_id)

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        # set run to terminated
        self._mlflow_client.set_terminated(run_id=self.run_id)

        # Remove run id
        logger.info("ending run: %s", self._run_id)
        self._storage_client.run_id = None
        self._active_run = None

    def _verify_active(self) -> None:
        if self._active_run is None:
            raise ValueError("ActiveRun has not been set")

    def register_card(self, card: cards.ArtifactCard, version_type: str = "minor"):
        """Register a given artifact card

        Args:
            card (Card): DataCard or ModelCard
            version_type (str): Version type for increment. Options are "major", "minor" and
            "patch". Defaults to "minor"
        """
        self._verify_active()
        card_type = card.__class__.__name__.lower()
        registry: CardRegistry = getattr(self.registries, card_type)
        registry.register_card(card=card, version_type=version_type)

    def load_card(self, card_type: str, info: cards.CardInfo) -> cards.ArtifactCard:
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

    def log_metric(self, key: str, value: float, timestamp: Optional[int] = None, step: Optional[int] = None) -> None:
        self._verify_active()
        self._mlflow_client.log_metric(run_id=self.run_id, key=key, value=value, timestamp=timestamp, step=step)

    @property
    def metrics(self) -> dict[str, float]:
        run_data: RunData = self._mlflow_client.get_run(self.run_id).data
        return run_data.metrics

    def log_param(self, key: str, value: str) -> None:
        self._verify_active()
        self._mlflow_client.log_param(run_id=self.run_id, key=key, value=value)

    @property
    def params(self) -> dict[str, str]:
        run_data: RunData = self._mlflow_client.get_run(self.run_id).data
        return run_data.params
