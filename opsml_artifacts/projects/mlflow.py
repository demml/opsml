# pylint: disable=invalid-envvar-value
import os
from contextlib import contextmanager
from typing import Iterator, Optional, TypeVar, cast
from dataclasses import dataclass
from mlflow.artifacts import download_artifacts
from mlflow.entities import RunStatus
from mlflow.entities import Run as MlflowRun
from mlflow.entities.run_data import RunData
from mlflow.entities.run_info import RunInfo as MlFlowRunInfo
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient
from mlflow.tracking.fluent import end_run as fluent_end_run
from pydantic import Field

from opsml_artifacts import CardRegistry, VersionType
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.helpers.types import OpsmlUri
from opsml_artifacts.projects.mlflow_utils import (
    get_card_registries,
    get_mlflow_client,
    mlflow_storage_client,
    set_env_vars,
    get_project_id,
    CardRegistries,
)
from opsml_artifacts.projects.types import Project, ProjectInfo, RunInfo
from opsml_artifacts.registry.cards import ArtifactCard, CardInfo
from opsml_artifacts.registry.storage.storage_system import MlflowStorageClient

logger = ArtifactLogger.get_logger(__name__)


# MlFlowProjectInfo -> Detail about project
# RunManager -> Manages active run and storage client (storage is tied to active run)
# MlFlowProject -> Requires MlFlowProjectInfo and uses a RunManager


@dataclass
class RunInfo:
    run_id: str
    storage_client: MlflowStorageClient
    mlflow_client: MlflowClient
    registries: CardRegistries
    run_name: Optional[str] = None


class MlflowProjectInfo(ProjectInfo):
    """
    An mlflow project identifier.

    Identifies a project with an mlflow backend. By default, projects in mlflow
    are "experiments". Each project is named after the team and project name
    with the convention "team:name".

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


class ActiveRun:
    def __init__(self, run_info: RunInfo):
        """
        Run object that handles CRUD for a given run of an MlFlowProject

        Args:
            run_info:
                Run info for a given active run
        """
        self._info = run_info
        self._active = True  # should be active upon instantiation

    @property
    def run_id(self) -> str:
        """Run id for current mlflow run"""
        return self._info.run_id

    @property
    def run_name(self) -> str:
        """Run id for current mlflow run"""
        return self._info.run_name

    @property
    def active(self) -> bool:
        return self._active

    def _verify_active(self):
        if not self.active:
            raise ValueError("""Run is not active""")

    def add_tag(self, key: str, value: str):
        """
        Adds a tag to the current project run

        Args:
            key:
                Name of the tag
            value:
                Value to associate with tag
        """

        self._info.mlflow_client.set_tag(
            run_id=self.run_id,
            key=key,
            value=value,
        )

    def register_card(self, card: ArtifactCard, version_type: VersionType = VersionType.MINOR):
        """
        Register a given artifact card.

        Args:
            card:
                The card to register
            version_type:
                Version type for increment. Options are "major", "minor" and
                "patch". Defaults to "minor".
        """
        self._verify_active()
        card_type = card.__class__.__name__.lower()
        registry: CardRegistry = getattr(self._info.registries, card_type)
        registry.register_card(card=card, version_type=version_type)

        tag_key = f"{card_type}-{card.name}"
        self.add_tag(
            key=tag_key,
            value=str(card.version),
        )

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        """
        Logs an artifact for the current run. All artifacts are loaded
        to a parent directory named "misc".

        Args:
            local_path:
                Local path to object
            artifact_path:
                Artifact directory path in Mlflow to log to. This path will be appended
                to parent directory "misc"
        Returns:
            None
        """
        self._verify_active()

        base_dir = "misc"
        if artifact_path is not None:
            artifact_path = f"{base_dir}/{artifact_path}"

        self._info.mlflow_client.log_artifact(
            run_id=self.run_id,
            local_path=local_path,
            artifact_path=artifact_path,
        )

    def log_metric(
        self,
        key: str,
        value: float,
        timestamp: Optional[int] = None,
        step: Optional[int] = None,
    ) -> None:
        """
        Log a metric for a given run

        Args:
            key:
                Metric name
            value:
                Metric value
            timestamp:
                Optional time indicating metric creation time
            step:
                Optional step in training when metric was created

        """
        self._verify_active()
        self._info.mlflow_client.log_metric(
            run_id=self.run_id,
            key=key,
            value=value,
            timestamp=timestamp,
            step=step,
        )

    def log_param(self, key: str, value: str) -> None:
        """
        Logs a parameter to project run

        Args:
            key:
                Parameter name
            value:
                Parameter value
        """

        self._verify_active()
        self._info.mlflow_client.log_param(run_id=self.run_id, key=key, value=value)


class RunManager:
    def __init__(
        self,
        mlflow_client: MlflowClient,
        project_id: str,
        project_info: MlflowProjectInfo,
        run_id: Optional[str] = None,
    ):
        """
        Manages runs for a given project including storing general attributes and creating, activating and
        ending runs. Also holds storage client needed to store artifacts associated with a run.

        Args:
            mlflow_client:
                MlflowClient instance
            project_id:
                Project identifier
            run_id:
                Optional project run id

        """

        # base attr
        self._project_id = project_id
        self._project_info = project_info
        self._run_id: Optional[str] = None
        self._run_name: Optional[str] = None
        self._active_run: Optional[ActiveRun] = None

        # needed for the magic
        self.mlflow_client = mlflow_client
        self.storage_client = self._get_storage_client()
        self.registries = get_card_registries(storage_client=self.storage_client)

        if run_id is not None:
            self._verify_run_id(run_id)
            self._run_id = run_id

    @property
    def run_id(self) -> Optional[str]:
        """Current Run id"""
        return self._run_id

    @run_id.setter
    def run_id(self, run_id: str):
        """Set Run id"""
        self._run_id = run_id

    @property
    def active_run(self) -> Optional[ActiveRun]:
        """Current active run"""
        return self._active_run

    @active_run.setter
    def active_run(self, active_run: ActiveRun):
        """Sets the active run"""
        self._active_run = active_run

    @property
    def run_name(self) -> Optional[str]:
        """Get current run name"""
        return self._run_name

    @run_name.setter
    def run_name(self, run_name: str) -> None:
        """Get current run name"""
        self._run_name = run_name

    def _get_storage_client(self) -> MlflowStorageClient:
        """Gets the MlflowStorageClient and sets the current client"""

        mlflow_storage_client.mlflow_client = self.mlflow_client
        return mlflow_storage_client

    def _verify_run_id(self, run_id: str) -> None:
        """Verifies the run exists for the given project."""
        try:
            self.mlflow_client.get_run(run_id)
        except MlflowException as exc:
            raise ValueError("Invalid run_id") from exc

    def _create_active_opsml_run(self):

        # Create opsml active run
        run_info = RunInfo(
            run_id=self.run_id,
            storage_client=self.storage_client,
            run_name=self.run_name,
            mlflow_client=self.mlflow_client,
            registries=self.registries,
        )

        self.active_run = ActiveRun(run_info=run_info)

    def _restore_run(self) -> None:
        """Restores a previous run to a running state"""
        self.mlflow_client.update_run(
            run_id=self.run_id,
            status=RunStatus.to_string(RunStatus.RUNNING),
        )

        # set mlflow run attributes
        mlflow_active_run = self.mlflow_client.get_run(self.run_id)
        self._set_run_attr(mlflow_active_run=mlflow_active_run)

        self._create_active_opsml_run()

    def _create_run(self, run_name: Optional[str] = None) -> None:
        """
        Create an mlflow run

        Args:
            run_name:
                Optional run name

        """
        tags = {
            "name": self._project_info.name,
            "team": self._project_info.team,
            "user_email": self._project_info.user_email,
        }
        mlflow_active_run = self.mlflow_client.create_run(
            experiment_id=self._project_id,
            run_name=run_name,
            tags=tags,
        )

        self._set_run_attr(mlflow_active_run=mlflow_active_run)
        self._create_active_opsml_run()

    def _set_run_attr(self, mlflow_active_run: MlflowRun) -> None:

        # Set run and name
        self.run_id = mlflow_active_run.info.run_id
        self.run_name = mlflow_active_run.info.run_name

        # update storage registry
        self._update_storage_client_run(mlflow_active_run)

        # needed for the fluent api (used with model logging)
        os.environ["MLFLOW_RUN_ID"] = str(self.run_id)

    def _set_active_run(self, run_name: Optional[str] = None) -> None:
        """
        Resolves and sets the active run for mlflow

        Args:
            run_name:
                Optional run name
        """

        if self.run_id is not None:
            return self._restore_run()
        return self._create_run(run_name=run_name)

    def _update_storage_client_run(self, mlflow_active_run: MlflowRun):
        self.storage_client.run_id = mlflow_active_run.info.run_id
        self.storage_client.artifact_path = mlflow_active_run.info.artifact_uri

    def verify_active(self) -> None:
        if self.active_run is None:
            raise ValueError("ActiveRun has not been set")

    def start_run(self, run_name: Optional[str] = None):
        """
        Starts an Mlflow run for a given project

        Args:
            run_name:
                Optional run name
        """

        if self.active_run is not None:
            raise ValueError("Could not start run. Another run is currently active")

        self._set_active_run(run_name=run_name)
        logger.info("starting run: %s", self.run_id)

    def _end_run(self) -> None:

        self.mlflow_client.set_terminated(run_id=self.run_id)

        # set to None
        self.storage_client.run_id = None
        self.active_run._active = False  # prevent use of detached run outside of context manager
        self.active_run = None  # detach active run

        # needed for when logging models (models are logged via fluent api)
        fluent_end_run()

    def end_run(self):
        """Ends an Mlflow run"""

        # Remove run id
        logger.info("ending run: %s", self.run_id)
        self._end_run()


class MlflowProject(Project):
    def __init__(self, info: MlflowProjectInfo):
        """
        Instantiates an mlflow project which log cards, metrics and params to
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
                    # If run_id is omitted, a new run is created.
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

        Args:
            info:
                Experiment information. if a run_id is given, that run is set
                as the project's current run.
        """

        tracking_uri = info.tracking_uri or os.getenv(OpsmlUri.TRACKING_URI)

        # dont want to expose mlflow client in project interface
        mlflow_client = get_mlflow_client(tracking_uri=tracking_uri)

        self._project_id = get_project_id(
            project_id=info.project_id,
            mlflow_client=mlflow_client,
        )

        # Set the run manager
        self._run_mgr = RunManager(
            run_id=info.run_id,
            project_id=self._project_id,
            mlflow_client=mlflow_client,
            project_info=info,
        )

        # work on this next PR - leaving so i remember
        # self._run_card = Optional[ExperimentCard] = None
        # if self._run_mgr.run_id is not None:
        # self.load_card(card_type="experiment", info)

    @property
    def run_id(self) -> str:
        """Current run id associated with project"""
        if self._run_mgr.run_id is not None:
            return self._run_mgr.run_id
        raise ValueError("Run id not set for current project")

    @property
    def project_id(self) -> str:
        return self._project_id

    @property
    def run_data(self) -> RunData:
        return self._mlflow_client.get_run(self.run_id).data

    @contextmanager
    def run(self, run_name: Optional[str] = None) -> ActiveRun:
        """
        Starts mlflow run for project

        Args:
            run_name:
                Optional run name
        """

        self._run_mgr.start_run(run_name=run_name)

        yield self._run_mgr.active_run

        self._run_mgr.end_run()

    def load_card(self, card_type: str, info: CardInfo) -> ArtifactCard:
        """
        Loads an ArtifactCard.

        Args:
            card_type:
                datacard or modelcard
            info:
                Card information to retrieve. `uid` takes precedence if it
                exists. If the optional `version` is specified, that version
                will be loaded. If it doesn't exist, the most recent ersion will
                be loaded.

        Returns
            `ArtifactCard`
        """
        registry: CardRegistry = getattr(self._run_mgr.registries, f"{card_type.lower()}card")
        return registry.load_card(name=info.name, team=info.team, version=info.version, uid=info.uid)

    def download_artifacts(
        self,
        artifact_path: Optional[str] = None,
        local_path: Optional[str] = None,
    ) -> str:
        """
        Download an artifact or artifacts associated with a run_id

        Args:
            artifact_path:
                Optional path that contains artifact(s) to download
            local_path:
                Local path (directory) to download artifacts to

        Returns:
            Artifact path
        """

        # ensure mlflow fluent sees env vars
        set_env_vars(tracking_uri=self._run_mgr.mlflow_client.tracking_uri)
        return download_artifacts(
            run_id=self.run_id,
            artifact_path=artifact_path,
            dst_path=local_path,
            tracking_uri=self._run_mgr.mlflow_client.tracking_uri,
        )

    @property
    def metrics(self) -> dict[str, float]:
        return self.run_data.metrics

    @property
    def params(self) -> dict[str, str]:
        return self.run_data.params

    @property
    def tags(self) -> dict[str, str]:
        return self.run_data.tags
