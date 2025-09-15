# type: ignore
# pylint: disable=redefined-builtin
from typing import Any, Dict, List, Optional, Protocol, TypeAlias, Union

from ..llm import Embedder, Prompt, Score
from ..profile import Histogram

class BaseModel(Protocol):
    """Protocol for pydantic BaseModel to ensure compatibility with context"""

    def model_dump(self) -> Dict[str, Any]:
        """Dump the model as a dictionary"""

    def model_dump_json(self) -> str:
        """Dump the model as a JSON string"""

    def __str__(self) -> str:
        """String representation of the model"""

SerializedType: TypeAlias = Union[str, int, float, dict, list]
Context: TypeAlias = Union[Dict[str, Any], BaseModel]

class LLMEvalTaskResult:
    """Eval Result for a specific evaluation"""

    @property
    def id(self) -> str:
        """Get the record id associated with this result"""

    @property
    def metrics(self) -> Dict[str, Score]:
        """Get the list of metrics"""

    @property
    def embedding(self) -> Dict[str, List[float]]:
        """Get embeddings of embedding targets"""

class LLMEvalResults:
    """Defines the results of an LLM eval metric"""

    def __getitem__(self, key: str) -> LLMEvalTaskResult:
        """Get the task results for a specific record ID. A RuntimeError will be raised if the record ID does not exist."""

    def __str__(self):
        """String representation of the LLMEvalResults"""

    def to_dataframe(self, polars: bool = False) -> Any:
        """
        Convert the results to a Pandas or Polars DataFrame.

        Args:
            polars (bool):
                Whether to return a Polars DataFrame. If False, a Pandas DataFrame will be returned.

        Returns:
            DataFrame:
                A Pandas or Polars DataFrame containing the results.
        """

    def model_dump_json(self) -> str:
        """Dump the results as a JSON string"""

    @staticmethod
    def model_validate_json(json_string: str) -> "LLMEvalResults":
        """Validate and create an LLMEvalResults instance from a JSON string

        Args:
            json_string (str):
                JSON string to validate and create the LLMEvalResults instance from.
        """

    @property
    def errored_tasks(self) -> List[str]:
        """Get a list of record IDs that had errors during evaluation"""

    @property
    def histograms(self) -> Optional[Dict[str, Histogram]]:
        """Get histograms for all calculated features (metrics, embeddings, similarities)"""

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

    @property
    def context(self) -> Dict[str, Any]:
        """Get the contextual information.

        Returns:
            The context data as a Python object (deserialized from JSON).
        """

def evaluate_llm(
    records: List[LLMEvalRecord],
    metrics: List[LLMEvalMetric],
    config: Optional[EvaluationConfig] = None,
) -> LLMEvalResults:
    """
    Evaluate LLM responses using the provided evaluation metrics.

    Args:
        records (List[LLMEvalRecord]):
            List of LLM evaluation records to evaluate.
        metrics (List[LLMEvalMetric]):
            List of LLMEvalMetric instances to use for evaluation.
        config (Optional[EvaluationConfig]):
            Optional EvaluationConfig instance to configure evaluation options.

    Returns:
        LLMEvalResults
    """

class EvaluationConfig:
    """Configuration options for LLM evaluation."""

    def __init__(
        self,
        embedder: Optional[Embedder] = None,
        embedding_targets: Optional[List[str]] = None,
        compute_similarity: bool = False,
        cluster: bool = False,
        compute_histograms: bool = False,
    ):
        """
        Initialize the EvaluationConfig with optional parameters.

        Args:
            embedder (Optional[Embedder]):
                Optional Embedder instance to use for generating embeddings for similarity-based metrics.
                If not provided, no embeddings will be generated.
            embedding_targets (Optional[List[str]]):
                Optional list of context keys to generate embeddings for. If not provided, embeddings will
                be generated for all string fields in the record context.
            compute_similarity (bool):
                Whether to compute similarity between embeddings. Default is False.
            cluster (bool):
                Whether to perform clustering on the embeddings. Default is False.
            compute_histograms (bool):
                Whether to compute histograms for all calculated features (metrics, embeddings, similarities).
                Default is False.
        """
