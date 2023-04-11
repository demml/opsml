import os
from typing import Optional

from mlflow.entities import Run as MlflowRun
from mlflow.entities import RunStatus
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient
from mlflow.tracking.fluent import end_run as fluent_end_run

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.projects.base._run_manager import _RunManager
from opsml_artifacts.projects.base.types import MlflowProjectInfo, Tags
from opsml_artifacts.projects.mlflow._active_run import MlflowActiveRun
from opsml_artifacts.projects.mlflow.mlflow_utils import (
    MlflowRunInfo,
    mlflow_storage_client,
)
from opsml_artifacts.registry.storage.storage_system import MlflowStorageClient

logger = ArtifactLogger.get_logger(__name__)


class _MlflowRunManager(_RunManager):
    def __init__(
        self,
        project_id: str,
        mlflow_client: MlflowClient,
        project_info: MlflowProjectInfo,
        run_id: Optional[str] = None,
    ):
        """
        Manages runs for a given project including storing general attributes and creating, activating and
        ending runs. Also holds storage client needed to store artifacts associated with a run.

        Args:
            project_id:
                Mlflow project identifier
            project_info:
                ProjectInfo
            run_id:
                Optional project run id

        """

        self.mlflow_client = mlflow_client
        self._project_id = project_id
        super().__init__(project_info, run_id)

    def _get_storage_client(self) -> MlflowStorageClient:
        """Gets the MlflowStorageClient and sets the current client"""

        mlflow_storage_client.mlflow_client = self.mlflow_client
        return mlflow_storage_client

    def _verify_run_id(self, run_id: str) -> None:
        """Verifies the run exists for the given project."""

        try:
            super()._verify_run_id(run_id=run_id)
            self.mlflow_client.get_run(run_id)
        except MlflowException as exc:
            raise ValueError("Invalid run_id") from exc

    def _create_active_opsml_run(self):
        """Creates and active run"""

        # Create opsml active run
        run_info = MlflowRunInfo(
            run_id=self.run_id,
            storage_client=self.storage_client,
            run_name=self.run_name,
            mlflow_client=self.mlflow_client,
            registries=self.registries,
            runcard=super()._load_runcard(),
        )

        self.active_run = MlflowActiveRun(run_info=run_info)

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
        mlflow_active_run = self.mlflow_client.create_run(
            experiment_id=self._project_id,
            run_name=run_name,
            tags=self.base_tags,
        )

        self._set_run_attr(mlflow_active_run=mlflow_active_run)
        self._create_active_opsml_run()
        self._active_run.add_tags(tags=self.base_tags)

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

    def _end_run(self) -> None:

        super()._end_run()
        self.mlflow_client.set_tag(run_id=self.run_id, key=Tags.VERSION, value=self.version)
        self.mlflow_client.set_terminated(run_id=self.run_id)

        # set to None
        self.storage_client.run_id = None

        # needed for when logging models (models are logged via fluent api)
        fluent_end_run()
