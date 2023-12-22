# pylint: disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, List, Optional, Union

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import TypeChecker
from opsml.registry.cards.base import ArtifactCard
from opsml.registry.sql.records import RegistryRecord, RunRegistryRecord
from opsml.registry.storage import client
from opsml.registry.storage.artifact import load_artifact_from_storage
from opsml.registry.types import (
    METRICS,
    PARAMS,
    AllowedDataType,
    ArtifactStorageSpecs,
    CardType,
    Metric,
    Param,
)

logger = ArtifactLogger.get_logger()


class RunCard(ArtifactCard):

    """
    Create a RunCard from specified arguments.

    Apart from required args, a RunCard must be associated with one of
    datacard_uid, modelcard_uids or pipelinecard_uid

    Args:
        name:
            Run name
        team:
            Team that this card is associated with
        user_email:
            Email to associate with card
        datacard_uid:
            Optional DataCard uid associated with pipeline
        modelcard_uids:
            Optional List of ModelCard uids to associate with this run
        pipelinecard_uid:
            Optional PipelineCard uid to associate with this experiment
        metrics:
            Optional dictionary of key (str), value (int, float) metric paris.
            Metrics can also be added via class methods.
        parameters:
            Parameters associated with a RunCard
        artifacts:
            Optional dictionary of artifacts (i.e. plots, reports) to associate
            with the current run.
        artifact_uris:
            Optional dictionary of artifact uris associated with artifacts.
        uid:
            Unique id (assigned if card has been registered)
        version:
            Current version (assigned if card has been registered)

    """

    datacard_uids: List[str] = []
    modelcard_uids: List[str] = []
    pipelinecard_uid: Optional[str] = None
    metrics: METRICS = {}
    parameters: PARAMS = {}
    artifacts: Dict[str, Any] = {}
    artifact_uris: Dict[str, str] = {}
    tags: Dict[str, str] = {}
    project_id: Optional[str] = None
    runcard_uri: Optional[str] = None

    def add_tag(self, key: str, value: str) -> None:
        """
        Logs params to current RunCard

        Args:
            key:
                Key for tag
            value:
                value for tag
        """
        self.tags = {**{key: value}, **self.tags}

    def add_tags(self, tags: Dict[str, str]) -> None:
        """
        Logs params to current RunCard

        Args:
            tags:
                Dictionary of tags
        """
        self.tags = {**tags, **self.tags}

    def log_parameters(self, params: Dict[str, Union[float, int, str]]) -> None:
        """
        Logs params to current RunCard

        Args:
            params:
                Dictionary of parameters
        """

        for key, value in params.items():
            # check key
            self.log_parameter(key, value)

    def log_parameter(self, key: str, value: Union[int, float, str]) -> None:
        """
        Logs params to current RunCard

        Args:
            key:
                Param name
            value:
                Param value
        """

        TypeChecker.check_param_type(param=value)
        param = Param(name=key, value=value)

        if self.parameters.get(key) is not None:
            self.parameters[key].append(param)

        else:
            self.parameters[key] = [param]

    def log_metric(
        self,
        key: str,
        value: Union[int, float],
        timestamp: Optional[int] = None,
        step: Optional[int] = None,
    ) -> None:
        """
        Logs metric to the existing RunCard metric dictionary

        Args:
            key:
                Metric name
            value:
                Metric value
            timestamp:
                Optional timestamp
            step:
                Optional step associated with name and value
        """

        TypeChecker.check_metric_type(metric=value)
        metric = Metric(name=key, value=value, timestamp=timestamp, step=step)

        if self.metrics.get(key) is not None:
            self.metrics[key].append(metric)
        else:
            self.metrics[key] = [metric]

    def log_metrics(self, metrics: Dict[str, Union[float, int]], step: Optional[int] = None) -> None:
        """
        Log metrics to the existing RunCard metric dictionary

        Args:
            metrics:
                Dictionary containing key (str) and value (float or int) pairs
                to add to the current metric set
            step:
                Optional step associated with metrics
        """

        for key, value in metrics.items():
            self.log_metric(key, value, step)

    def log_artifact(self, name: str, artifact: Any) -> None:
        """
        Append any artifact associated with your run to
        the RunCard. The artifact will be saved and the uri
        will be appended to the RunCard. Artifact must be pickleable
        (saved with joblib)

        Args:
            name:
                Artifact name
            artifact:
                Artifact
        """

        new_artifact = {name: artifact}
        self.artifacts = {**new_artifact, **self.artifacts}
        setattr(self, "artifacts", {**new_artifact, **self.artifacts})

    def create_registry_record(self, **kwargs: Dict[str, Any]) -> RegistryRecord:
        """Creates a registry record from the current RunCard"""

        exclude_attr = {"artifacts", "params", "metrics"}

        return RunRegistryRecord(**{**self.model_dump(exclude=exclude_attr), **kwargs})

    def add_artifact_uri(self, name: str, uri: str) -> None:
        """
        Adds an artifact_uri to the runcard

        Args:
            name:
                Name to associate with artifact
            uri:
                Uri where artifact is stored
        """

        self.artifact_uris[name] = uri

    def add_card_uid(self, card_type: str, uid: str) -> None:
        """
        Adds a card uid to the appropriate card uid list for tracking

        Args:
            card_type:
                ArtifactCard class name
            uid:
                Uid of registered ArtifactCard
        """

        if card_type == CardType.DATACARD:
            self.datacard_uids = [uid, *self.datacard_uids]
        elif card_type == CardType.MODELCARD:
            self.modelcard_uids = [uid, *self.modelcard_uids]

    def get_metric(self, name: str) -> Union[List[Metric], Metric]:
        """
        Gets a metric by name

        Args:
            name:
                Name of metric

        Returns:
            List of dictionaries or dictionary containing value

        """
        metric = self.metrics.get(name)
        if metric is not None:
            if len(metric) > 1:
                return metric
            if len(metric) == 1:
                return metric[0]
            return metric

        raise ValueError(f"Metric {metric} is not defined")

    def get_parameter(self, name: str) -> Union[List[Param], Param]:
        """
        Gets a metric by name

        Args:
            name:
                Name of param

        Returns:
            List of dictionaries or dictionary containing value

        """
        param = self.parameters.get(name)
        if param is not None:
            if len(param) > 1:
                return param
            if len(param) == 1:
                return param[0]
            return param

        raise ValueError(f"Param {param} is not defined")

    def load_artifacts(self) -> None:
        if bool(self.artifact_uris):
            for name, uri in self.artifact_uris.items():
                self.artifacts[name] = load_artifact_from_storage(
                    artifact_type=AllowedDataType.DICT,
                    storage_client=client.storage_client,
                    storage_spec=ArtifactStorageSpecs(save_path=uri),
                )
            return None

        logger.info("No artifact uris associated with RunCard")
        return None

    @property
    def card_type(self) -> str:
        return CardType.RUNCARD.value
