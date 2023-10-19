# pylint: disable=invalid-envvar-value
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from contextlib import contextmanager
from typing import Iterator, List, Optional, Union, cast

from mlflow.artifacts import download_artifacts
from mlflow.entities.run_data import RunData

# helpers
from opsml.helpers.logging import ArtifactLogger

# projects
from opsml.projects.base.project import OpsmlProject
from opsml.projects.base.types import ProjectInfo
from opsml.projects.mlflow._active_run import MlflowActiveRun
from opsml.projects.mlflow._run_manager import _MlflowRunManager
from opsml.registry.cards.types import METRICS, PARAMS, Metric, Param

logger = ArtifactLogger.get_logger()


class MlflowProject(OpsmlProject):
    def __init__(self, info: ProjectInfo):  # pylint: disable=super-init-not-called
        """
        Instantiates an mlflow project which log cards, metrics and params to
        the opsml registry and mlflow via a "run" object.

        If info.run_id is set, that run_id will be loaded as read only. In read
        only mode, you can retrieve cards, metrics, and params, however you
        cannot write new data. If you wish to record data/create a new run, you will
        need to enter the run context.

        Example:

            ```python
            project: MlFlowProject = get_project(
                ProjectInfo(
                    name="test-project",
                    team="devops-ml",
                    # If run_id is omitted, a new run is created.
                    run_id="123ab123kaj8u8naskdfh813",
                )
            )
            # the project is in "read only" mode. all read operations will work
            for k, v in project.params:
                logger.info("{} = {}", k, v)

            # creating a project run
            with project.run() as run:
                # Now that the run context is entered, it's in read/write mode
                # You can write cards, params, and metrics to the project.
                run.log_parameter(key="my_param", value="12.34")
            ```

        Args:
            info:
                Run information. if a run_id is given, that run is set
                as the project's current run.
        """

        # Set RunManager
        self._run_mgr = _MlflowRunManager(project_info=info)

    @property
    def run_data(self) -> RunData:
        """Returns all `RunData` associated with a Run"""
        return self._run_mgr.mlflow_client.get_run(self.run_id).data  # type: ignore

    @contextmanager
    def run(self, run_name: Optional[str] = None) -> Iterator[MlflowActiveRun]:
        """
        Starts mlflow run for project

        Args:
            run_name:
                Optional run name
        """

        self._run_mgr.start_run(run_name=run_name)

        try:
            yield cast(MlflowActiveRun, self._run_mgr.active_run)
        except Exception as error:
            logger.error("Error encountered. Ending run. {}", error)
            self._run_mgr.end_run()
            raise error

        self._run_mgr.end_run()

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
        return download_artifacts(
            run_id=self.run_id,
            artifact_path=artifact_path,
            dst_path=local_path,
            tracking_uri=self._run_mgr.mlflow_client.tracking_uri,  # type: ignore
        )

    def list_artifacts(self, path: Optional[str] = None) -> dict[str, float]:
        """List artifacts for the current run"""
        return self._run_mgr.mlflow_client.list_artifacts(  # type: ignore
            run_id=self.run_id,
            path=path,
        )

    @property
    def metrics(self) -> METRICS:
        """Returns a Run's metrics

        Example:
            ```python
            info = ProjectInfo(name="opsml", team="devops",user_email="test_email",run_id=run.run_id)
            project = MlflowProject(info=info)
            project.metrics

            {
                'test': [Metric(name='test', value=99.0, step=None, timestamp=None)],
                'r2': [Metric(name='r2', value=0.006525740117159562, step=None, timestamp=None)],
                'mae': [Metric(name='mae', value=2.225978693518221, step=None, timestamp=None)]
            }

            ```
        """

        metrics: METRICS = {}
        for key, value in self.run_data.metrics.items():
            metrics[key] = [Metric(name=key, value=value)]  # keep consistency with RunCard type
        return metrics

    def get_metric(self, name: str) -> Union[List[Metric], Metric]:
        """
        Get metric by name

        Args:
            name: str

        Returns:
            `Metric`

        """
        metric = self.metrics.get(name)

        if metric is not None:
            return metric[0]

        raise ValueError(f"Metric {name} not found")

    @property
    def parameters(self) -> PARAMS:
        """Returns a Run's parameters"""
        params: PARAMS = {}
        for key, value in self.run_data.params.items():
            params[key] = [Param(name=key, value=value)]
        return params

    def get_parameter(self, name: str) -> Union[List[Param], Param]:
        """
        Get param by name

        Args:
            name: str

        Returns:
            `Param`

        """
        param = self.parameters.get(name)
        if param is not None:
            return param[0]

        raise ValueError(f"Param {name} not found")

    @property
    def tags(self) -> dict[str, str]:
        """Returns a Run's tags"""
        return self.run_data.tags
