# type: ignore

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Protocol, TypeAlias, Union

from ..card import DataCard, ExperimentCard, ModelCard, PromptCard
from ..data import DataSaveKwargs
from ..llm import Prompt, Score
from ..model import ModelSaveKwargs
from ..types import VersionType

class Experiment:
    def start_experiment(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        code_dir: Optional[Path] = None,
        log_hardware: bool = False,
        experiment_uid: Optional[str] = None,
    ) -> "Experiment":
        """
        Start an Experiment

        Args:
            space (str | None):
                space to associate with `ExperimentCard`
            name (str | None):
                Name to associate with `ExperimentCard`
            code_dir (Path | None):
                Directory to log code from
            log_hardware (bool):
                Whether to log hardware information or not
            experiment_uid (str | None):
                Experiment UID. If provided, the experiment will be loaded from the server.

        Returns:
            Experiment
        """

    def __enter__(self) -> "Experiment":
        pass

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

    def log_metric(
        self,
        name: str,
        value: float,
        step: Optional[int] = None,
        timestamp: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        """
        Log a metric

        Args:
            name (str):
                Name of the metric
            value (float):
                Value of the metric
            step (int | None):
                Step of the metric
            timestamp (int | None):
                Timestamp of the metric
            created_at (datetime | None):
                Created at of the metric
        """

    def log_metrics(self, metrics: list[Metric]) -> None:
        """
        Log multiple metrics

        Args:
            metrics (list[Metric]):
                List of metrics to log
        """

    def log_eval_metrics(self, metrics: "EvalMetrics") -> None:
        """
        Log evaluation metrics

        Args:
            metrics (EvalMetrics):
                Evaluation metrics to log
        """

    def log_parameter(
        self,
        name: str,
        value: Union[int, float, str],
    ) -> None:
        """
        Log a parameter

        Args:
            name (str):
                Name of the parameter
            value (int | float | str):
                Value of the parameter
        """

    def log_parameters(
        self, parameters: list[Parameter] | Dict[str, Union[int, float, str]]
    ) -> None:
        """
        Log multiple parameters

        Args:
            parameters (list[Parameter] | Dict[str, Union[int, float, str]]):
                Parameters to log
        """

    def log_artifact(
        self,
        lpath: Path,
        rpath: Optional[str] = None,
    ) -> None:
        """
        Log an artifact

        Args:
            lpath (Path):
                The local path where the artifact has been saved to
            rpath (Optional[str]):
                The path to associate with the artifact in the experiment artifact directory
                {experiment_path}/artifacts. If not provided, defaults to
                {experiment}/artifacts/{filename}
        """

    def log_figure_from_path(
        self,
        lpath: Path,
        rpath: Optional[str] = None,
    ) -> None:
        """
        Log a figure

        Args:
            lpath (Path):
                The local path where the figure has been saved to. Must be an image type
                (e.g. jpeg, tiff, png, etc.)
            rpath (Optional[str]):
                The path to associate with the figure in the experiment artifact directory
                {experiment_path}/artifacts/figures. If not provided, defaults to
                {experiment}/artifacts/figures/{filename}

        """

    def log_figure(
        self, name: str, figure: Any, kwargs: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a figure. This method will log a matplotlib Figure object to the experiment artifacts.

        Args:
            name (str):
                Name of the figure including its file extension
            figure (Any):
                Figure to log
            kwargs (Optional[Dict[str, Any]]):
                Additional keyword arguments
        """

    def log_artifacts(
        self,
        paths: Path,
    ) -> None:
        """
        Log multiple artifacts

        Args:
            paths (Path):
                Paths to a directory containing artifacts.
                All files in the directory will be logged.
        """

    @property
    def card(self) -> "ExperimentCard":
        """
        ExperimentCard associated with the Experiment
        """

    def register_card(
        self,
        card: Union[DataCard, ModelCard, PromptCard],
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs: Optional[ModelSaveKwargs | DataSaveKwargs] = None,
    ) -> None:
        """Register a Card as part of an experiment

        Args:
            card (DataCard | ModelCard):
                Card to register. Can be a DataCard or a ModelCard
            version_type (VersionType):
                How to increment the version SemVer. Default is VersionType.Minor.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.
            save_kwargs (SaveKwargs):
                Optional SaveKwargs to pass to the Card interface (If using DataCards
                and ModelCards).

        """

def start_experiment(
    space: Optional[str] = None,
    name: Optional[str] = None,
    code_dir: Optional[Path] = None,
    log_hardware: bool = False,
    experiment_uid: Optional[str] = None,
) -> Experiment:
    """
    Start an Experiment

    Args:
        space (str | None):
            space to associate with `ExperimentCard`
        name (str | None):
            Name to associate with `ExperimentCard`
        code_dir (Path | None):
            Directory to log code from
        log_hardware (bool):
            Whether to log hardware information or not
        experiment_uid (str | None):
            Experiment UID. If provided, the experiment will be loaded from the server.

    Returns:
        Experiment
    """

class LLMEvalMetric:
    """Defines an LLM eval metric to use when evaluating LLMs"""

    def __init__(self, name: str, prompt: Prompt):
        """
        Initialize an LLMEvalMetric to use for evaluating LLMs. This is
        most commonly used in conjunction with `evaluate_llm` where LLM inputs
        and responses can be evaluated against a variety of user-defined metrics.

        Args:
            name (str):
                Name of the metric
            prompt (Prompt):
                Prompt to use for the metric. For example, a user may create
                an accuracy analysis prompt or a query reformulation analysis prompt.
        """

    def __str__(self) -> str:
        """
        String representation of the LLMEvalMetric
        """

class EvalResult:
    """Eval Result for a specific evaluation"""

    @property
    def error(self) -> Optional[str]: ...
    @property
    def tasks(self) -> Dict[str, Score]: ...
    @property
    def id(self) -> str: ...
    def __getitem__(self, key: str) -> Score:
        """
        Get the score for a specific task
        """
        ...

class LLMEvalResults:
    """Defines the results of an LLM eval metric"""

    def __getitem__(self, key: str) -> float:
        """Get the value` of the metric by name. A RuntimeError will be raised if the metric does not exist."""
        ...

    def __iter__(self) -> Iterator[EvalResult]:
        """Get an iterator over the metric names and values."""
        ...

class Metric:
    def __init__(
        self,
        name: str,
        value: float,
        step: Optional[int] = None,
        timestamp: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        """
        Initialize a Metric

        Args:
            name (str):
                Name of the metric
            value (float):
                Value of the metric
            step (int | None):
                Step of the metric
            timestamp (int | None):
                Timestamp of the metric
            created_at (datetime | None):
                Created at of the metric
        """

    @property
    def name(self) -> str:
        """
        Name of the metric
        """

    @property
    def value(self) -> float:
        """
        Value of the metric
        """

    @property
    def step(self) -> Optional[int]:
        """
        Step of the metric
        """

    @property
    def timestamp(self) -> Optional[int]:
        """
        Timestamp of the metric
        """

    @property
    def created_at(self) -> Optional[datetime]:
        """
        Created at of the metric
        """

class EvalMetrics:
    """
    Map of metrics used that can be used to evaluate a model.
    The metrics are also used when comparing a model with other models
    """

    def __init__(self, metrics: Dict[str, float]) -> None:
        """
        Initialize EvalMetrics

        Args:
            metrics (Dict[str, float]):
                Dictionary of metrics containing the name of the metric as the key and its value as the value.
        """

    def __getitem__(self, key: str) -> float:
        """Get the value of a metric by name. A RuntimeError will be raised if the metric does not exist."""
        ...

class Metrics:
    def __str__(self): ...
    def __getitem__(self, index: int) -> Metric: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...

class Parameters:
    def __str__(self): ...
    def __getitem__(self, index: int) -> Parameter: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...

class Parameter:
    def __init__(
        self,
        name: str,
        value: Union[int, float, str],
    ) -> None:
        """
        Initialize a Parameter

        Args:
            name (str):
                Name of the parameter
            value (int | float | str):
                Value of the parameter
        """

    @property
    def name(self) -> str:
        """
        Name of the parameter
        """

    @property
    def value(self) -> Union[int, float, str]:
        """
        Value of the parameter
        """

def get_experiment_metrics(
    experiment_uid: str,
    names: Optional[list[str]] = None,
) -> Metrics:
    """
    Get metrics of an experiment

    Args:
        experiment_uid (str):
            UID of the experiment
        names (list[str] | None):
            Names of the metrics to get. If None, all metrics will be returned.

    Returns:
        Metrics
    """

def get_experiment_parameters(
    experiment_uid: str,
    names: Optional[list[str]] = None,
) -> Parameters:
    """
    Get parameters of an experiment

    Args:
        experiment_uid (str):
            UID of the experiment
        names (list[str] | None):
            Names of the parameters to get. If None, all parameters will be returned.

    Returns:
        Parameters
    """

class BaseModel(Protocol):
    """Protocol for pydantic BaseModel to ensure compatibility with context"""

    def model_dump(self) -> Dict[str, Any]:
        """Dump the model as a dictionary"""
        ...

    def model_dump_json(self) -> str:
        """Dump the model as a JSON string"""
        ...

    def __str__(self) -> str:
        """String representation of the model"""
        ...

SerializedType: TypeAlias = Union[str, int, float, dict, list]
Context: TypeAlias = Union[Dict[str, Any], BaseModel]

class LLMEvalRecord:
    """LLM record containing context tied to a Large Language Model interaction
    that is used to evaluate LLM responses.


    Examples:
        >>> record = LLMEvalRecord(
                id="123",
                context={
                    "input": "What is the capital of France?",
                    "response": "Paris is the capital of France."
                },
        ... )
        >>> print(record.context["input"])
        "What is the capital of France?"
    """

    def __init__(
        self,
        context: Context,
        id: Optional[str] = None,
    ) -> None:
        """Creates a new LLM record to associate with an `LLMDriftProfile`.
        The record is sent to the `Scouter` server via the `ScouterQueue` and is
        then used to inject context into the evaluation prompts.

        Args:
            context:
                Additional context information as a dictionary or a pydantic BaseModel. During evaluation,
                this will be merged with the input and response data and passed to the assigned
                evaluation prompts. So if you're evaluation prompts expect additional context via
                bound variables (e.g., `${foo}`), you can pass that here as key value pairs.
                {"foo": "bar"}
            id:
                Unique identifier for the record. If not provided, a new UUID will be generated.
                This is helpful for when joining evaluation results back to the original request.

        Raises:
            TypeError: If context is not a dict or a pydantic BaseModel.

        """
        ...

    @property
    def context(self) -> Dict[str, Any]:
        """Get the contextual information.

        Returns:
            The context data as a Python object (deserialized from JSON).

        Raises:
            TypeError: If the stored JSON cannot be converted to a Python object.
        """
        ...

def evaluate_llm(
    records: List[LLMEvalRecord],
    metrics: List[LLMEvalMetric],
) -> LLMEvalResults:
    """
    Evaluate LLM responses using the provided evaluation metrics.

    Args:
        records (List[LLMEvalRecord]):
            List of LLM evaluation records to evaluate.
        metrics (List[LLMEvalMetric]):
            List of LLMEvalMetric instances to use for evaluation.

    Returns:
        LLMEvalResults
    """
