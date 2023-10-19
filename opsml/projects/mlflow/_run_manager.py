# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from typing import Optional

from mlflow.entities import Run as MlflowRun
from mlflow.entities import RunStatus
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient
from mlflow.tracking.fluent import end_run as fluent_end_run

from opsml.helpers.logging import ArtifactLogger
from opsml.projects.base._run_manager import _RunManager
from opsml.projects.base.types import ProjectInfo, Tags
from opsml.projects.mlflow._active_run import MlflowActiveRun
from opsml.projects.mlflow.mlflow_utils import MlflowRunInfo, set_env_vars
from opsml.registry.utils.settings import settings
from opsml.registry.storage.storage_system import MlflowStorageClient

logger = ArtifactLogger.get_logger()

mlflow_storage = MlflowStorageClient(storage_settings=settings.storage_settings)
mlflow_storage.opsml_storage_client = settings.storage_client


class _MlflowRunManager(_RunManager):
    def __init__(self, project_info: ProjectInfo):
        """
        Manages runs for a given project including storing general attributes and creating, activating and
        ending runs. Also holds storage client needed to store artifacts associated with a run.

        Args:
            project_info:
                ProjectInfo

        """

        # set env vars here in case user wants to change tracking URI on subsequent runs (you never know ¯\_(ツ)_/¯)
        set_env_vars(tracking_uri=project_info.tracking_uri)
        self.mlflow_client = MlflowClient(tracking_uri=project_info.tracking_uri)

        super().__init__(project_info)

        # set mlflow client for storage client to use (use same mlflow client that run uses)
        # Reminder: Once routes for uploading objects are written for the opsml server,
        # we can remove MlflowStorageClient class
        self.registries.set_storage_client(storage_client=mlflow_storage)
        self._storage_client = mlflow_storage
        self._storage_client.mlflow_client = self.mlflow_client

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
            base_artifact_uri=self.storage_client.artifact_path,
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
        self.active_run.add_tags(tags=self.base_tags)

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
        # need to switch back to original storage client in order to save/update runcard
        self.registries.set_storage_client(storage_client=settings.storage_client)
        super()._end_run()
        self.mlflow_client.set_tag(run_id=self.run_id, key=Tags.MLFLOW_VERSION, value=self.version)

        self.mlflow_client.set_terminated(run_id=self.run_id)

        # set to None
        self.storage_client.run_id = None

        # needed for when logging models (models are logged via fluent api)
        fluent_end_run()

    def _get_project_id(self) -> str:
        """
        Finds the project_id from mlflow for the given project. If an
        existing project does not exist, a new one is created.

        Args:
            project_id:
                Project identifier
            mlflow_client:
                MlflowClient instance

        Returns:
            The underlying mlflow project_id
        """

        super()._get_project_id()

        # REMINDER: We treat mlflow "experiments" as projects
        project = self.mlflow_client.get_experiment_by_name(
            name=self._project_info.project_id,
        )
        if project is None:
            return self.mlflow_client.create_experiment(name=self._project_info.project_id)
        return project.experiment_id
