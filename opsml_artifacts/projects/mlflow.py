# pylint: disable=invalid-envvar-value
import os
from contextlib import contextmanager
from typing import Iterator, Optional, TypeVar, cast

from mlflow.artifacts import download_artifacts
from mlflow.entities import Run, RunStatus
from mlflow.entities.run_data import RunData
from mlflow.entities.run_info import RunInfo
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
)
from opsml_artifacts.projects.types import Project, ProjectInfo
from opsml_artifacts.registry.cards import ArtifactCard, CardInfo
from opsml_artifacts.registry.storage.storage_system import MlFlowStorageClient

logger = ArtifactLogger.get_logger(__name__)


# MlFlowProjectInfo -> Detail about project
# RunManager -> Manages active run and storage client (storage is tied to active run)
# MlFlowProject -> Requires MlFlowProjectInfo and uses a RunManager
_Self = TypeVar("_Self", bound="MlFlowProject")


class MlFlowProjectInfo(ProjectInfo):
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


class RunManager:
    def __init__(
        self,
        mlflow_client: MlflowClient,
        project_id: str,
        run_id: Optional[str] = None,
    ):
        """
        Manages a run for a given project. Also holds storage client needed to
        store artifacts associated for a run.

        Args:
            mlflow_client:
                MlflowClient instance
            project_id:
                Project identifier
            run_id:
                Optional project run id

        """

        self._mlflow_client = mlflow_client
        self._project_id = project_id
        self._run_id: Optional[str] = None
        self._active_run: Optional[Run] = None
        self._run_name: Optional[str] = None
        self._storage_client = self._get_storage_client()

        if run_id is not None:
            self._verify_run_id(run_id)
            self._run_id = run_id

    @property
    def run_id(self) -> Optional[str]:
        """Run id for current mlflow run"""
        return self._run_id

    @run_id.setter
    def run_id(self, run_id: str) -> None:
        """Sets run id"""
        self._run_id = run_id

    @property
    def active_run(self) -> Optional[Run]:
        """Active run for current mlflow run"""
        return self._active_run

    @active_run.setter
    def active_run(self, active_run: Run) -> None:
        """Sets active run"""
        self._active_run = active_run

    @property
    def run_name(self) -> Optional[str]:
        """Get current run name"""
        return self._run_name

    @run_name.setter
    def run_name(self, run_name: str) -> None:
        """Get current run name"""
        self._run_name = run_name

    @property
    def artifact_save_path(self) -> str:
        """Returns the path where artifacts are saved."""
        self.verify_active()

        info: RunInfo = cast(Run, self.active_run).info
        return info.artifact_uri

    def _get_storage_client(self) -> MlFlowStorageClient:
        """Gets the MlFlowStorageClient and sets the current client"""

        mlflow_storage_client.mlflow_client = self._mlflow_client
        return mlflow_storage_client

    def _verify_run_id(self, run_id: str) -> Run:
        """Verifies the run exists for the given project."""
        try:
            self._mlflow_client.get_run(run_id)
        except MlflowException as exc:
            raise ValueError("Invalid run_id") from exc

    def _restore_run(self) -> None:
        """Restores a previous run to a running state"""
        self._mlflow_client.update_run(
            run_id=self.run_id,
            status=RunStatus.to_string(RunStatus.RUNNING),
        )
        self.active_run = self._mlflow_client.get_run(self.run_id)

        self._set_run_attr()

    def _create_run(self, run_name: Optional[str] = None) -> None:
        """
        Create an mlflow run

        Args:
            run_name:
                Optional run name

        """
        self.active_run = self._mlflow_client.create_run(
            experiment_id=self._project_id,
            run_name=run_name,
        )

        self._set_run_attr()

    def _set_run_attr(self) -> None:
        run = cast(Run, self.active_run)
        self.run_id = run.info.run_id
        self.run_name = run.info.run_name

        # update storage registry
        self._update_storage_client_run()

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

    def _update_storage_client_run(self):
        self._storage_client.run_id = self.run_id
        self._storage_client.artifact_path = self.artifact_save_path

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

        self._mlflow_client.set_terminated(run_id=self.run_id)

        # set to None
        self._storage_client.run_id = None
        self.active_run = None

        # needed for when logging models (models are logged via fluent api)
        fluent_end_run()

    def end_run(self):
        """Ends an Mlflow run"""

        # Remove run id
        logger.info("ending run: %s", self.run_id)
        self._end_run()


class MlFlowProject(Project):
    def __init__(self, info: MlFlowProjectInfo):
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
        self._mlflow_client = get_mlflow_client(tracking_uri=tracking_uri)
        self._project_id = self._get_project_id(project_id=info.project_id)

        self._run_mgr = RunManager(
            run_id=info.run_id,
            project_id=self._project_id,
            mlflow_client=self._mlflow_client,
        )
        self.registries = get_card_registries(storage_client=self._run_mgr._storage_client)

        # work on this next PR
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

    def _verify_active(self):
        return self._run_mgr.verify_active()

    def _get_project_id(self, project_id: str) -> str:
        """
        Finds the project_id from mlflow for the given project. If an
        existing proejct does not exist, a new one is created.

        Args:
            project_id:
                Project identifier

        Returns:
            The underlying mlflow project_id
        """
        # REMINDER: We treat mlflow "experiments" as projects

        project = self._mlflow_client.get_experiment_by_name(name=project_id)
        if project is None:
            return self._mlflow_client.create_experiment(name=project_id)
        return project.experiment_id

    @contextmanager
    def run(self: _Self, run_name: Optional[str] = None) -> Iterator[_Self]:
        """
        Starts mlflow run for project

        Args:
            run_name:
                Optional run name
        """

        self._run_mgr.start_run(run_name=run_name)

        yield self

        self._run_mgr.end_run()

    def add_tag(self, key: str, value: str):
        """
        Adds a tag to the current project run

        Args:
            key:
                Name of the tag
            value:
                Value to associate with tag
        """

        self._mlflow_client.set_tag(
            run_id=self.run_id,
            key=key,
            value=value,
        )

    # def _update_experiment_card(self):

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
        registry: CardRegistry = getattr(self.registries, card_type)
        registry.register_card(card=card, version_type=version_type)

        tag_key = f"{card_type}-{card.name}"
        self.add_tag(
            key=tag_key,
            value=str(card.version),
        )

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
        registry: CardRegistry = getattr(self.registries, f"{card_type.lower()}card")
        return registry.load_card(name=info.name, team=info.team, version=info.version, uid=info.uid)

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

        self._mlflow_client.log_artifact(
            run_id=self.run_id,
            local_path=local_path,
            artifact_path=artifact_path,
        )

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
        set_env_vars(tracking_uri=self._mlflow_client.tracking_uri)
        return download_artifacts(
            run_id=self.run_id,
            artifact_path=artifact_path,
            dst_path=local_path,
            tracking_uri=self._mlflow_client.tracking_uri,
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

    @property
    def tags(self) -> dict[str, str]:
        run_data: RunData = self._mlflow_client.get_run(self.run_id).data
        return run_data.tags
