# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pylint: disable=invalid-name


import tempfile
import uuid
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import joblib
import numpy as np
from numpy.typing import NDArray
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
    GraphStyle,
    Metric,
    Metrics,
    Param,
    Params,
    RegistryTableNames,
    RegistryType,
    RunCardRegistry,
    RunGraph,
    SaveName,
)

logger = ArtifactLogger.get_logger()

_List = List[Union[float, int]]
_Dict = Dict[str, List[Union[float, int]]]
_YReturn = Union[_List, _Dict]
_ParseReturn = Tuple[_YReturn, str]


def _dump_graph_artifact(graph: RunGraph, name: str, uri: Path) -> Tuple[Path, Path]:
    """Helper method for saving graph artifacts to storage

    Args:
        graph:
            RunGraph object
        name:
            Name of graph
        uri:
            Uri to store graph artifact
    """
    with tempfile.TemporaryDirectory() as tempdir:
        lpath = Path(tempdir) / f"{name}.joblib"
        rpath = (uri / SaveName.GRAPHS.value) / lpath.name
        joblib.dump(graph.model_dump(), lpath)

        client.storage_client.put(lpath, rpath)

        return lpath, rpath


def _decimate_list(array: List[Union[float, int]]) -> List[Union[float, int]]:
    """Decimates array to no more than 200,000 points

    Args:
        array:
            List of floats or ints

    Returns:
        Decimated array
    """
    length = len(array)
    if len(array) > 200_000:
        step = round(length / 200_000)
        return array[::step]

    return array


def _parse_y_to_list(
    x_length: int,
    y: Union[List[Union[float, int]], NDArray[Any], Dict[str, Union[List[Union[float, int]], NDArray[Any]]]],
) -> _ParseReturn:
    """Helper method for parsing y to list when logging a graph

    Args:
        x_length:
            Length of x
        y:
            Y values to parse. Can be a list, dictionary or numpy array

    Returns:
        List or dictionary of y values

    """
    # if y is dictionary
    if isinstance(y, dict):
        _y: Dict[str, List[Union[float, int]]] = {}

        # common sense constraint
        if len(y.keys()) > 50:
            raise ValueError("Too many keys in dictionary. A maximum of 50 keys for y is allowed.")

        for k, v in y.items():
            if isinstance(v, np.ndarray):
                v = v.flatten().tolist()
                assert isinstance(v, list), "y must be a list or dictionary"
                v = _decimate_list(v)

            assert x_length == len(v), "x and y must be the same length"
            _y[k] = v

        return _y, "multi"

    # if y is ndarray
    if isinstance(y, np.ndarray):
        y = y.flatten().tolist()
        assert isinstance(y, list), "y must be a list or dictionary"

        y = _decimate_list(y)
        assert x_length == len(y), "x and y must be the same length"

        return y, "single"

    # if y is list
    assert isinstance(y, list), "y must be a list or dictionary"
    y = _decimate_list(y)
    assert x_length == len(y), "x and y must be the same length"
    return y, "single"


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
        Logs tags to current RunCard

        Args:
            key:
                Key for tag
            value:
                value for tag
        """
        self.tags = {**{key: value}, **self.tags}

    def add_tags(self, tags: Dict[str, str]) -> None:
        """
        Logs tags to current RunCard

        Args:
            tags:
                Dictionary of tags
        """
        self.tags = {**tags, **self.tags}

    def log_graph(
        self,
        name: str,
        x: Union[List[Union[float, int]], NDArray[Any]],
        y: Union[List[Union[float, int]], NDArray[Any], Dict[str, Union[List[Union[float, int]], NDArray[Any]]]],
        y_label: str,
        x_label: str,
        graph_style: str,
    ) -> None:
        """Logs a graph to the RunCard, which will be rendered in the UI as a line graph

        Args:
            name:
                Name of graph
            x:
                List or numpy array of x values

            x_label:
                Label for x axis
            y:
                Either a list or numpy array of y values or a dictionary of y values where key is the group label and
                value is a list or numpy array of y values
            y_label:
                Label for y axis
            graph_style:
                Style of graph. Options are "line" or "scatter"

        example:

            ### single line graph
            x = np.arange(1, 400, 0.5)
            y = x * x
            run.log_graph(name="graph1", x=x, y=y, x_label="x", y_label="y", graph_style="line")

            ### multi line graph
            x = np.arange(1, 1000, 0.5)
            y1 = x * x
            y2 = y1 * 1.1
            y3 = y2 * 3
            run.log_graph(
                name="multiline",
                x=x,
                y={"y1": y1, "y2": y2, "y3": y3},
                x_label="x",
                y_label="y",
                graph_style="line",
            )

        """

        if isinstance(x, np.ndarray):
            x = x.flatten().tolist()
            assert isinstance(x, list), "x must be a list or dictionary"

        x = _decimate_list(x)

        parsed_y, graph_type = _parse_y_to_list(len(x), y)

        logger.info(f"Logging graph {name} to RunCard")
        graph = RunGraph(
            name=name,
            x=x,
            x_label=x_label,
            y=parsed_y,
            y_label=y_label,
            graph_type=graph_type,
            graph_style=GraphStyle.from_str(graph_style).value,  # validate graph style
        )

        # save graph to storage so we can view in ui while run is active
        lpath, rpath = _dump_graph_artifact(graph, name, self.uri)

        self._add_artifact_uri(
            name=name,
            local_path=lpath.as_posix(),
            remote_path=rpath.as_posix(),
        )

    def log_parameters(self, parameters: Dict[str, Union[float, int, str]]) -> None:
        """
        Logs parameters to current RunCard

        Args:
            parameters:
                Dictionary of parameters
        """

        for key, value in parameters.items():
            # check key
            self.log_parameter(key, value)

    def log_parameter(self, key: str, value: Union[int, float, str]) -> None:
        """
        Logs parameter to current RunCard

        Args:
            key:
                Param name
            value:
                Param value
        """

        TypeChecker.check_param_type(param=value)
        _key = TypeChecker.replace_spaces(key)

        param = Param(name=key, value=value)

        if self.parameters.get(_key) is not None:
            self.parameters[_key].append(param)

        else:
            self.parameters[_key] = [param]

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
        _key = TypeChecker.replace_spaces(key)

        metric = Metric(name=_key, value=value, timestamp=timestamp, step=step)

        self._registry.insert_metric([{**metric.model_dump(), **{"run_uid": self.uid}}])

        if self.metrics.get(_key) is not None:
            self.metrics[_key].append(metric)
        else:
            self.metrics[_key] = [metric]

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

        exclude_attr = {"parameters", "metrics"}

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
        _key = TypeChecker.replace_spaces(name)

        metric = self.metrics.get(_key)

        if metric is None:
            # try to get metric from registry
            assert self.uid is not None, "RunCard must be registered to get metric"
            _metric = self._registry.get_metric(run_uid=self.uid, name=[_key])

            if _metric is not None:
                metric = [Metric(**i) for i in _metric]

            else:
                raise ValueError(f"Metric {metric} was not defined")

        if len(metric) > 1:
            return metric
        if len(metric) == 1:
            return metric[0]
        return metric

    def load_metrics(self) -> None:
        """Reloads metrics from registry"""
        assert self.uid is not None, "RunCard must be registered to load metrics"

        metrics = self._registry.get_metric(run_uid=self.uid)

        if metrics is None:
            logger.info("No metrics found for RunCard")
            return None

        # reset metrics
        self.metrics = {}
        for metric in metrics:
            _metric = Metric(**metric)
            if _metric.name not in self.metrics:
                self.metrics[_metric.name] = [_metric]
            else:
                self.metrics[_metric.name].append(_metric)
        return None

    def get_parameter(self, name: str) -> Union[List[Param], Param]:
        """
        Gets a parameter by name

        Args:
            name:
                Name of parameter

        Returns:
            List of dictionaries or dictionary containing value

        """
        _key = TypeChecker.replace_spaces(name)
        param = self.parameters.get(_key)
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
        if self.version == CommonKwargs.BASE_VERSION.value:
            if self.uid is None:
                self.uid = uuid.uuid4().hex

            end_path = self.uid
        else:
            end_path = f"v{self.version}"

        return Path(
            config.storage_root,
            RegistryTableNames.from_str(self.card_type).value,
            str(self.repository),
            str(self.name),
            end_path,
        )

    @cached_property
    def _registry(self) -> RunCardRegistry:
        from opsml.registry.backend import _set_registry

        return cast(RunCardRegistry, _set_registry(RegistryType.RUN))

    @property
    def card_type(self) -> str:
        return CardType.RUNCARD.value
