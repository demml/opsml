# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import model_validator

from opsml.cards.base import ArtifactCard
from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import TypeChecker
from opsml.settings.config import config
from opsml.storage import client
from opsml.types import (
    Artifact,
    ArtifactUris,
    CardType,
    CommonKwargs,
    Metric,
    Metrics,
    Param,
    Params,
    RegistryTableNames,
    SaveName,
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
        repository:
            Repository that this card is associated with
        contact:
            Contact to associate with card
        info:
            `CardInfo` object containing additional metadata. If provided, it will override any
            values provided for `name`, `repository`, `contact`, and `version`.

            Name, repository, and contact are required arguments for all cards. They can be provided
            directly or through a `CardInfo` object.

        datacard_uids:
            Optional DataCard uids associated with this run
        modelcard_uids:
            Optional List of ModelCard uids to associate with this run
        pipelinecard_uid:
            Optional PipelineCard uid to associate with this experiment
        metrics:
            Optional dictionary of key (str), value (int, float) metric paris.
            Metrics can also be added via class methods.
        parameters:
            Parameters associated with a RunCard
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
    metrics: Metrics = {}
    parameters: Params = {}
    artifact_uris: ArtifactUris = {}
    tags: Dict[str, Union[str, int]] = {}
    project: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_defaults_args(cls, card_args: Dict[str, Any]) -> Dict[str, Any]:
        # add default
        contact = card_args.get("contact")

        if contact is None:
            card_args["contact"] = CommonKwargs.UNDEFINED.value

        repository = card_args.get("repository")

        if repository is None:
            card_args["repository"] = "opsml"

        return card_args

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

    def log_artifact_from_file(
        self,
        name: str,
        local_path: Union[str, Path],
        artifact_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """
        Log a local file or directory to the opsml server and associate with the current run.

        Args:
            name:
                Name to assign to artifact(s)
            local_path:
                Local path to file or directory. Can be string or pathlike object
            artifact_path:
                Optional path to store artifact in opsml server. If not provided, 'artifacts' will be used
        """

        lpath = Path(local_path)
        rpath = self.uri / (artifact_path or SaveName.ARTIFACTS.value)

        if lpath.is_file():
            rpath = rpath / lpath.name

        client.storage_client.put(lpath, rpath)
        self._add_artifact_uri(
            name=name,
            local_path=lpath.as_posix(),
            remote_path=rpath.as_posix(),
        )

    def create_registry_record(self) -> Dict[str, Any]:
        """Creates a registry record from the current RunCard"""

        exclude_attr = {"params", "metrics"}

        return self.model_dump(exclude=exclude_attr)

    def _add_artifact_uri(self, name: str, local_path: str, remote_path: str) -> None:
        """
        Adds an artifact_uri to the runcard

        Args:
            name:
                Name to associate with artifact
            uri:
                Uri where artifact is stored
        """

        self.artifact_uris[name] = Artifact(
            name=name,
            local_path=local_path,
            remote_path=remote_path,
        )

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

    def load_artifacts(self, name: Optional[str] = None) -> None:
        """Loads artifacts from artifact_uris"""
        if bool(self.artifact_uris) is False:
            logger.info("No artifact uris associated with RunCard")
            return None

        if name is not None:
            artifact = self.artifact_uris.get(name)
            assert artifact is not None, f"Artifact {name} not found"
            client.storage_client.get(
                Path(artifact.remote_path),
                Path(artifact.local_path),
            )

        else:
            for _, artifact in self.artifact_uris.items():
                client.storage_client.get(
                    Path(artifact.remote_path),
                    Path(artifact.local_path),
                )
        return None

    @property
    def uri(self) -> Path:
        """The base URI to use for the card and it's artifacts."""

        # when using runcard outside of run context
        if self.version is None:
            if self.uid is None:
                self.uid = uuid.uuid4().hex

            end_path = self.uid
        else:
            end_path = f"v{self.version}"

        return Path(
            config.storage_root,
            RegistryTableNames.from_str(self.card_type).value,
            self.repository,
            self.name,
            end_path,
        )

    @property
    def card_type(self) -> str:
        return CardType.RUNCARD.value
