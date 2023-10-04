# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Dict, Optional, Union, cast
from pathlib import Path
import os
from opsml.projects.base._active_run import ActiveRun
from opsml.projects.mlflow.mlflow_utils import MlflowRunInfo
from opsml.registry.cards.types import METRICS, PARAMS


class MlflowActiveRun(ActiveRun):
    def __init__(self, run_info: MlflowRunInfo):
        super().__init__(run_info)

        self._info = cast(MlflowRunInfo, self._info)

    @property
    def info(self):
        return cast(MlflowRunInfo, self._info)

    def add_tag(self, key: str, value: str):
        """
        Adds a tag to the current run
        Args:
            key:
                Name of the tag
            value:
                Value to associate with tag
        """

        super().add_tag(key, value)
        self.info.mlflow_client.set_tag(
            run_id=self.run_id,
            key=key,
            value=value,
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
        super().log_metric(key, value, timestamp, step)

        self.info.mlflow_client.log_metric(
            run_id=self.run_id,
            key=key,
            value=value,
            timestamp=timestamp,
            step=step,
        )

    def log_metrics(
        self,
        metrics: Dict[str, Union[float, int]],
        step: Optional[int] = None,
    ):
        """Logs a collection of metrics for a run

        Args:
            metrics:
                Dictionary of metrics
            step:
                step the metrics are associated with

        """
        super().log_metrics(metrics, step)
        for key, value in metrics.items():
            self.info.mlflow_client.log_metric(run_id=self.run_id, key=key, value=value, step=step)

    def log_parameter(self, key: str, value: str) -> None:
        """
        Logs a parameter to project run

        Args:
            key:
                Parameter name
            value:
                Parameter value
        """

        self._verify_active()
        super().log_parameter(key, value)
        self.info.mlflow_client.log_param(run_id=self.run_id, key=key, value=value)

    def log_artifact_from_file(self, local_path: Union[os.PathLike, str], artifact_path: Optional[str] = None) -> None:
        """
        Logs an artifact for the current run. All artifacts are loaded
        to a parent directory named "misc".

        Args:
            local_path:
                Local path to object. Can be a string of `Path` object
            artifact_path:
                Artifact directory path in Mlflow to log to. This path will be appended
                to parent directory "misc"
        """
        self._verify_active()

        _artifact_path = "misc"

        if artifact_path is not None:
            _artifact_path = f"{_artifact_path}/{artifact_path}"

        self.info.mlflow_client.log_artifact(
            run_id=self.run_id,
            local_path=local_path,
            artifact_path=_artifact_path,
        )

        filename = local_path.name if isinstance(local_path, Path) else Path(local_path).name
        artifact_uri = f"{self.info.base_artifact_path}/{_artifact_path}/{filename}"

        self.runcard.add_artifact_uri(name=filename, uri=artifact_uri)

    @property
    def run_data(self):
        return self.info.mlflow_client.get_run(self.run_id).data

    @property
    def metrics(self) -> METRICS:
        return self.run_data.metrics

    @property
    def parameters(self) -> PARAMS:
        return self.run_data.parameters

    @property
    def tags(self) -> dict[str, str]:
        return self.run_data.tags
