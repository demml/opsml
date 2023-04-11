from dataclasses import dataclass
from typing import Optional, cast

from opsml_artifacts.projects.base._active_run import ActiveRun
from opsml_artifacts.projects.mlflow.mlflow_utils import MlflowRunInfo


class MlflowActiveRun(ActiveRun):
    def __init__(self, run_info: MlflowRunInfo):
        super().__init__(run_info)

        self._info = cast(MlflowRunInfo, self._info)

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
        self._info.mlflow_client.set_tag(
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
        super().log_param(key, value)
        self._info.mlflow_client.log_param(run_id=self.run_id, key=key, value=value)

    @property
    def run_data(self):
        return self._info.mlflow_client.get_run(self.run_id).data

    @property
    def metrics(self) -> dict[str, float]:
        return self.run_data.metrics

    @property
    def params(self) -> dict[str, str]:
        return self.run_data.params

    @property
    def tags(self) -> dict[str, str]:
        return self.run_data.tags
