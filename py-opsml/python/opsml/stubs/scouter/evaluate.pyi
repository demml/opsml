#### begin imports ####
# ty:ignore[unresolved-import]

from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    TypeVar,
    Union,
    overload,
)

from ..header import SerializedType
from ..agent.potato import Prompt
from .scouter import (
    AgentEvalProfile,
    ComparisonResults,
    EvalRecord,
    EvalResults,
    EvaluationConfig,
    ScouterQueue,
)
from .tracing import BaseTracer, TraceSpan

#### end of imports ####

class EvaluationTaskType:
    """Types of evaluation tasks for LLM assessments."""

    Assertion: "EvaluationTaskType"
    """Assertion-based evaluation task."""
    LLMJudge: "EvaluationTaskType"
    """LLM judge-based evaluation task."""
    HumanValidation: "EvaluationTaskType"
    """Human validation evaluation task."""
    TraceAssertion: "EvaluationTaskType"
    """Trace assertion-based evaluation task."""
    AgentAssertion: "EvaluationTaskType"
    """Agent assertion-based evaluation task."""

class ComparisonOperator:
    """Comparison operators for assertion-based evaluations.

    Defines the available comparison operators that can be used to evaluate
    assertions against expected values in LLM evaluation workflows.

    Examples:
        >>> operator = ComparisonOperator.GreaterThan
        >>> operator = ComparisonOperator.Equal
    """

    Equals: "ComparisonOperator"
    """Equality comparison (==)"""

    NotEqual: "ComparisonOperator"
    """Inequality comparison (!=)"""

    GreaterThan: "ComparisonOperator"
    """Greater than comparison (>)"""

    GreaterThanOrEqual: "ComparisonOperator"
    """Greater than or equal comparison (>=)"""

    LessThan: "ComparisonOperator"
    """Less than comparison (<)"""

    LessThanOrEqual: "ComparisonOperator"
    """Less than or equal comparison (<=)"""

    Contains: "ComparisonOperator"
    """Contains substring or element (in)"""

    NotContains: "ComparisonOperator"
    """Does not contain substring or element (not in)"""

    StartsWith: "ComparisonOperator"
    """Starts with substring"""

    EndsWith: "ComparisonOperator"
    """Ends with substring"""

    Matches: "ComparisonOperator"
    """Matches regular expression pattern"""

    HasLengthGreaterThan: "ComparisonOperator"
    """Has specified length greater than"""

    HasLengthLessThan: "ComparisonOperator"
    """Has specified length less than"""

    HasLengthEqual: "ComparisonOperator"
    """Has specified length equal to"""

    HasLengthGreaterThanOrEqual: "ComparisonOperator"
    """Has specified length greater than or equal to"""

    HasLengthLessThanOrEqual: "ComparisonOperator"
    """Has specified length less than or equal to"""

    # type validations
    IsNumeric: "ComparisonOperator"
    """Is a numeric value"""

    IsString: "ComparisonOperator"
    """Is a string value"""

    IsBoolean: "ComparisonOperator"
    """Is a boolean value"""

    IsNull: "ComparisonOperator"
    """Is null (None) value"""

    IsArray: "ComparisonOperator"
    """Is an array (list) value"""

    IsObject: "ComparisonOperator"
    """Is an object (dict) value"""

    IsEmail: "ComparisonOperator"
    """Is a valid email format"""

    IsUrl: "ComparisonOperator"
    """Is a valid URL format"""

    IsUuid: "ComparisonOperator"
    """Is a valid UUID format"""

    IsIso8601: "ComparisonOperator"
    """Is a valid ISO 8601 date format"""

    IsJson: "ComparisonOperator"
    """Is a valid JSON format"""

    MatchesRegex: "ComparisonOperator"
    """Matches a regular expression pattern"""

    InRange: "ComparisonOperator"
    """Is within a specified numeric range"""

    NotInRange: "ComparisonOperator"
    """Is outside a specified numeric range"""

    IsPositive: "ComparisonOperator"
    """Is a positive number"""

    IsNegative: "ComparisonOperator"
    """Is a negative number"""
    IsZero: "ComparisonOperator"
    """Is zero"""

    SequenceMatches: "ComparisonOperator"
    """Check that span sequence matches the expected ordered list."""

    ContainsAll: "ComparisonOperator"
    """Contains all specified elements"""

    ContainsAny: "ComparisonOperator"
    """Contains any of the specified elements"""

    ContainsNone: "ComparisonOperator"
    """Contains none of the specified elements"""

    IsEmpty: "ComparisonOperator"
    """Is empty"""

    IsNotEmpty: "ComparisonOperator"
    """Is not empty"""

    HasUniqueItems: "ComparisonOperator"
    """Has unique items"""

    IsAlphabetic: "ComparisonOperator"
    """Is alphabetic"""

    IsAlphanumeric: "ComparisonOperator"
    """Is alphanumeric"""

    IsLowerCase: "ComparisonOperator"
    """Is lowercase"""

    IsUpperCase: "ComparisonOperator"
    """Is uppercase"""

    ContainsWord: "ComparisonOperator"
    """Contains a specific word"""

    ApproximatelyEquals: "ComparisonOperator"
    """Approximately equals within a tolerance"""

class AssertionTask:
    """Assertion-based evaluation task for LLM monitoring.

    Defines a rule-based assertion that evaluates values extracted from LLM
    context/responses against expected conditions without requiring additional LLM calls.
    Assertions are efficient, deterministic evaluations ideal for validating
    structured outputs, checking thresholds, or verifying data constraints.

    Assertions can operate on:
        - Nested fields via dot-notation paths (e.g., "response.user.age")
        - Top-level context values when context_path is None
        - String, numeric, boolean, or collection values

    Common Use Cases:
        - Validate response structure ("response.status" == "success")
        - Check numeric thresholds ("response.confidence" >= 0.8)
        - Verify required fields exist ("response.user.id" is not None)
        - Validate string patterns ("response.language" contains "en")

    Examples:
        Basic numeric comparison:

        >>> # Context at runtime: {"response": {"user": {"age": 25}}}
        >>> task = AssertionTask(
        ...     id="check_user_age",
        ...     context_path="response.user.age",
        ...     operator=ComparisonOperator.GreaterThan,
        ...     expected_value=18,
        ...     description="Verify user is an adult"
        ... )

        Checking top-level fields:

        >>> # Context at runtime: {"user": {"age": 25}}
        >>> task = AssertionTask(
        ...     id="check_age",
        ...     context_path="user.age",
        ...     operator=ComparisonOperator.GreaterThanOrEqual,
        ...     expected_value=21,
        ...     description="Check minimum age requirement"
        ... )

        Operating on entire context (no nested path):

        >>> # Context at runtime: 25
        >>> task = AssertionTask(
        ...     id="age_threshold",
        ...     context_path=None,
        ...     operator=ComparisonOperator.GreaterThan,
        ...     expected_value=18,
        ...     description="Validate age value"
        ... )

        String validation:

        >>> # Context: {"response": {"status": "completed"}}
        >>> task = AssertionTask(
        ...     id="status_check",
        ...     context_path="response.status",
        ...     operator=ComparisonOperator.Equals,
        ...     expected_value="completed",
        ...     description="Verify completion status"
        ... )

        Collection membership:

        >>> # Context: {"response": {"tags": ["valid", "processed"]}}
        >>> task = AssertionTask(
        ...     id="tag_validation",
        ...     context_path="response.tags",
        ...     operator=ComparisonOperator.Contains,
        ...     expected_value="valid",
        ...     description="Check for required tag"
        ... )

        With dependencies:

        >>> task = AssertionTask(
        ...     id="confidence_check",
        ...     context_path="response.confidence",
        ...     operator=ComparisonOperator.GreaterThan,
        ...     expected_value=0.9,
        ...     description="High confidence validation",
        ...     depends_on=["status_check"]
        ... )

    Note:
        - Field paths use dot-notation for nested access
        - Field paths are case-sensitive
        - When context_path is None, the entire context is used as the value
        - Type mismatches between actual and expected values will fail the assertion
        - Dependencies are executed before this task
    """

    def __init__(
        self,
        id: str,
        expected_value: Any,
        operator: ComparisonOperator,
        context_path: Optional[str] = None,
        item_context_path: Optional[str] = None,
        description: Optional[str] = None,
        depends_on: Optional[Sequence[str]] = None,
        condition: bool = False,
    ):
        """Initialize an assertion task for rule-based evaluation.

        Args:
            id:
                Unique identifier for the task. Will be converted to lowercase.
                Used to reference this task in dependencies and results.
            expected_value:
                The expected value to compare against. Can be any JSON-serializable
                type: str, int, float, bool, list, dict, or None.
            operator:
                Comparison operator to use for the assertion. Must be a
                ComparisonOperator enum value.
            context_path:
                Optional dot-notation path to extract value from context
                (e.g., "response.user.age"). If None, the entire context
                is used as the comparison value.
            item_context_path:
                Optional dot-notation path applied to each element when
                `context_path` resolves to an array of objects. For example,
                if `context_path="responses"` yields
                `[{"text": "hello"}, {"text": "world"}]`, setting
                `item_context_path="text"` causes the operator to be evaluated
                against the `"text"` value of every element.
            description:
                Optional human-readable description of what this assertion validates.
                Useful for understanding evaluation results.
            depends_on:
                Optional list of task IDs that must complete successfully before
                this task executes. Empty list if not provided.
            condition:
                If True, this assertion task acts as a condition for subsequent tasks.
                If the assertion fails, dependent tasks will be skipped and this task
                will be excluded from final results.

        Raises:
            TypeError: If expected_value is not JSON-serializable or if operator
                is not a valid ComparisonOperator.
        """

    @property
    def id(self) -> str:
        """Unique task identifier (lowercase)."""

    @id.setter
    def id(self, id: str) -> None:
        """Set task identifier (will be converted to lowercase)."""

    @property
    def context_path(self) -> Optional[str]:
        """Dot-notation path to field in context, or None for entire context."""

    @context_path.setter
    def context_path(self, context_path: Optional[str]) -> None:
        """Set context path for value extraction."""

    @property
    def item_context_path(self) -> Optional[str]:
        """Dot-notation path applied to each array element when context_path resolves to an array of objects."""

    @item_context_path.setter
    def item_context_path(self, item_context_path: Optional[str]) -> None:
        """Set item context path for per-element extraction during array evaluation."""

    @property
    def operator(self) -> ComparisonOperator:
        """Comparison operator for the assertion."""

    @operator.setter
    def operator(self, operator: ComparisonOperator) -> None:
        """Set comparison operator."""

    @property
    def expected_value(self) -> Any:
        """Expected value for comparison.

        Returns:
            The expected value as a Python object (deserialized from internal
            JSON representation).
        """

    @property
    def description(self) -> Optional[str]:
        """Human-readable description of the assertion."""

    @description.setter
    def description(self, description: Optional[str]) -> None:
        """Set assertion description."""

    @property
    def depends_on(self) -> List[str]:
        """List of task IDs this task depends on."""

    @depends_on.setter
    def depends_on(self, depends_on: List[str]) -> None:
        """Set task dependencies."""

    @property
    def condition(self) -> bool:
        """Indicates if this task is a condition for subsequent tasks."""

    @condition.setter
    def condition(self, condition: bool) -> None:
        """Set whether this task is a condition for subsequent tasks."""

    @property
    def task_type(self) -> EvaluationTaskType:
        """The type of this evaluation task (Assertion)."""

    def __str__(self) -> str:
        """Return string representation of the assertion task."""

class LLMJudgeTask:
    """LLM-powered evaluation task for complex assessments.

    Uses an additional LLM call to evaluate responses based on sophisticated
    criteria that require reasoning, context understanding, or subjective judgment.
    LLM judges are ideal for evaluations that cannot be captured by deterministic
    rules, such as semantic similarity, quality assessment, or nuanced criteria.

    Unlike AssertionTask which provides efficient, deterministic rule-based evaluation,
    LLMJudgeTask leverages an LLM's reasoning capabilities for:
        - Semantic similarity and relevance assessment
        - Quality, coherence, and fluency evaluation
        - Factual accuracy and hallucination detection
        - Tone, sentiment, and style analysis
        - Custom evaluation criteria requiring judgment
        - Complex reasoning over multiple context elements

    The LLM judge executes a prompt that receives context (either raw or from
    dependencies) and returns a response that is then compared against the expected
    value using the specified operator.

    Common Use Cases:
        - Evaluate semantic similarity between generated and reference answers
        - Assess response quality on subjective criteria (helpfulness, clarity)
        - Detect factual inconsistencies or hallucinations
        - Score tone appropriateness for different audiences
        - Judge whether responses meet complex, nuanced requirements

    Examples:
        Basic relevance check using LLM judge:

        >>> # Define a prompt that evaluates relevance
        >>> relevance_prompt = Prompt(
        ...     system_instructions="Evaluate if the response is relevant to the query",
        ...     messages="Given the query '{{query}}' and response '{{response}}', rate the relevance from 0 to 10 as an integer.",
        ...     model="gpt-4",
        ...     provider= Provider.OpenAI,
        ...     output_type=Score # returns a structured output with schema {"score": float, "reason": str}
        ... )

        >>> # Context at runtime: {"query": "What is AI?", "response": "AI is..."}
        >>> task = LLMJudgeTask(
        ...     id="relevance_judge",
        ...     prompt=relevance_prompt,
        ...     expected_value=8,
        ...     context_path="score",
        ...     operator=ComparisonOperator.GreaterThanOrEqual,
        ...     description="Ensure response relevance score >= 8"
        ... )

        Factuality check with structured output:

        >>> # Prompt returns a Pydantic model with factuality assessment
        >>> from pydantic import BaseModel
        >>> class FactCheckResult(BaseModel):
        ...     is_factual: bool
        ...     confidence: float

        >>> fact_check_prompt = Prompt(
        ...     system_instructions="Verify factual claims in the response",
        ...     messages="Assess the factual accuracy of the response: '{{response}}'. Provide a JSON with fields 'is_factual' (bool) and 'confidence' (float).", # pylint: disable=line-too-long
        ...     model="gpt-4",
        ...     provider= Provider.OpenAI,
        ...     output_type=FactCheckResult
        ... )

        >>> # Context: {"response": "Paris is the capital of France"}
        >>> task = LLMJudgeTask(
        ...     id="fact_checker",
        ...     prompt=fact_check_prompt,
        ...     expected_value={"is_factual": True, "confidence": 0.95},
        ...     context_path="response",
        ...     operator=ComparisonOperator.Contains
        ... )

        Quality assessment with dependencies:

        >>> # This judge depends on previous relevance check
        >>> quality_prompt = Prompt(
        ...     system_instructions="Assess the overall quality of the response",
        ...     messages="Given the response '{{response}}', rate its quality from 0 to 5",
        ...     model="gemini-3.0-flash",
        ...     provider= Provider.Google,
        ...     output_type=Score
        ... )

        >>> task = LLMJudgeTask(
        ...     id="quality_judge",
        ...     prompt=quality_prompt,
        ...     expected_value=0.7,
        ...     context_path=None,
        ...     operator=ComparisonOperator.GreaterThan,
        ...     depends_on=["relevance_judge"],
        ...     description="Evaluate overall quality after relevance check"
        ... )
    Note:
        - LLM judge tasks incur additional latency and cost vs assertions
        - Scouter does not auto-inject any additional prompts or context apart from what is defined
          in the Prompt object
        - For tasks that contain dependencies, upstream results are passed as context to downstream tasks.
        - Use dependencies to chain evaluations and pass results between tasks
        - max_retries helps handle transient LLM failures (defaults to 3)
        - Field paths work the same as AssertionTask (dot-notation for nested access)
        - Consider cost/latency tradeoffs when designing judge evaluations
    """

    def __init__(
        self,
        id: str,
        prompt: Prompt[Any],
        expected_value: Any,
        context_path: Optional[str],
        operator: ComparisonOperator,
        description: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        max_retries: Optional[int] = None,
        condition: bool = False,
    ):
        """Initialize an LLM judge task for advanced evaluation.

        Creates an evaluation task that uses an LLM to assess responses based on
        sophisticated criteria requiring reasoning or subjective judgment. The LLM
        receives context (raw or from dependencies) and returns a response that
        is compared against the expected value.

        Args:
            id (str):
                Unique identifier for the task. Will be converted to lowercase.
                Used to reference this task in dependencies and results.
            prompt (Prompt):
                Prompt configuration defining the LLM evaluation task.
            expected_value (Any):
                The expected value to compare against the LLM's response. Type depends
                on prompt response type. Can be any JSON-serializable type: str, int,
                float, bool, list, dict, or None.
            context_path (Optional[str]):
                Optional dot-notation path to extract value from context before passing
                to the LLM prompt (e.g., "response.text"), the entire response will be
                evaluated.
            operator (ComparisonOperator):
                Comparison operator to apply between LLM response and expected_value
            description (Optional[str]):
                Optional human-readable description of what this judge evaluates.
            depends_on (Optional[List[str]]):
                Optional list of task IDs that must complete successfully before this
                task executes. Results from dependencies are passed to the LLM prompt
                as additional context parameters. Empty list if not provided.
            max_retries (Optional[int]):
                Optional maximum number of retry attempts if the LLM call fails
                (network errors, rate limits, etc.). Defaults to 3 if not provided.
                Set to 0 to disable retries.
            condition (bool):
                If True, this judge task acts as a condition for subsequent tasks.
                If the judge fails, dependent tasks will be skipped and this task
                will be excluded from final results.
        """

    @property
    def id(self) -> str:
        """Unique task identifier (lowercase)."""

    @id.setter
    def id(self, id: str) -> None:
        """Set task identifier (will be converted to lowercase)."""

    @property
    def prompt(self) -> Prompt:
        """Prompt configuration for the LLM evaluation task.

        Defines the LLM model, evaluation instructions, and response format.
        The prompt must have response_type of Score or Pydantic.
        """

    @property
    def context_path(self) -> Optional[str]:
        """Dot-notation path to extract value from context before LLM evaluation.

        If specified, extracts nested value from context (e.g., "response.text")
        and passes it to the LLM prompt. If None, the entire context or
        dependency results are passed.
        """

    @property
    def operator(self) -> ComparisonOperator:
        """Comparison operator for evaluating LLM response against expected value.

        For Score responses: use numeric operators (GreaterThan, Equals, etc.)
        For Pydantic responses: use structural operators (Contains, Equals, etc.)
        """

    @property
    def expected_value(self) -> Any:
        """Expected value to compare against LLM response.

        Returns:
            The expected value as a Python object (deserialized from internal
            JSON representation).
        """

    @property
    def depends_on(self) -> List[str]:
        """List of task IDs this task depends on.

        Dependency results are passed to the LLM prompt as additional context
        parameters, enabling chained evaluations.
        """

    @depends_on.setter
    def depends_on(self, depends_on: List[str]) -> None:
        """Set task dependencies."""

    @property
    def max_retries(self) -> Optional[int]:
        """Maximum number of retry attempts for LLM call failures.

        Handles transient failures like network errors or rate limits.
        Defaults to 3 if not specified during initialization.
        """

    @max_retries.setter
    def max_retries(self, max_retries: Optional[int]) -> None:
        """Set maximum retry attempts."""

    @property
    def condition(self) -> bool:
        """Indicates if this task is a condition for subsequent tasks."""

    @condition.setter
    def condition(self, condition: bool) -> None:
        """Set whether this task is a condition for subsequent tasks."""

    @property
    def task_type(self) -> EvaluationTaskType:
        """The type of this evaluation task (LLMJudge)."""

    def __str__(self) -> str:
        """Return string representation of the LLM judge task."""

class SpanStatus:
    """Status codes for trace spans.

    Represents the execution status of a span within a distributed trace,
    following OpenTelemetry status conventions.

    Examples:
        >>> status = SpanStatus.Ok
        >>> error_status = SpanStatus.Error
    """

    Ok: "SpanStatus"
    """Span completed successfully without errors."""

    Error: "SpanStatus"
    """Span encountered an error during execution."""

    Unset: "SpanStatus"
    """Span status has not been explicitly set."""

class AggregationType:
    """Aggregation operations for span attribute values.

    Defines how numeric or collection values should be aggregated across
    multiple spans matching a filter. Used in TraceAssertion.span_aggregation
    to compute statistics over filtered spans.

    Examples:
        >>> # Compute average duration across LLM spans
        >>> aggregation = AggregationType.Average
        >>>
        >>> # Count total spans matching filter
        >>> count = AggregationType.Count
    """

    Count: "AggregationType"
    """Count the number of spans matching the filter."""

    Sum: "AggregationType"
    """Sum numeric attribute values across spans."""

    Average: "AggregationType"
    """Calculate mean of numeric attribute values."""

    Min: "AggregationType"
    """Find minimum numeric attribute value."""

    Max: "AggregationType"
    """Find maximum numeric attribute value."""

    First: "AggregationType"
    """Get attribute value from first matching span (by start time)."""

    Last: "AggregationType"
    """Get attribute value from last matching span (by start time)."""

class SpanFilter:
    """Filter for selecting specific spans within a trace.

    Provides composable filtering logic to identify spans based on name,
    attributes, status, duration, or combinations thereof. Filters can be
    combined using and() and or() methods for complex queries.

    SpanFilter is used to target specific spans for assertions in
    TraceAssertionTask, enabling precise behavioral validation.

    Examples:
        Filter by exact span name:

        >>> filter = SpanFilter.by_name("llm.generate")

        Filter by name pattern (regex):

        >>> filter = SpanFilter.by_name_pattern(r"retry.*")

        Filter spans with specific attribute:

        >>> filter = SpanFilter.with_attribute("model")

        Filter spans with attribute value (note: requires PyValueWrapper):

        >>> # Note: In Python, pass native types; they're converted internally
        >>> # This is handled automatically by the with_attribute_value method
        >>> filter = SpanFilter.with_attribute_value("model", "gpt-4")

        Filter by span status:

        >>> filter = SpanFilter.with_status(SpanStatus.Error)

        Filter by duration constraints:

        >>> filter = SpanFilter.with_duration(min_ms=100, max_ms=5000)

        Combine filters with AND logic:

        >>> base = SpanFilter.by_name_pattern("llm.*")
        >>> with_model = base.and_(SpanFilter.with_attribute("model"))
        >>> # Matches spans: name matches "llm.*" AND has "model" attribute

        Combine filters with OR logic:

        >>> retries = SpanFilter.by_name_pattern("retry.*")
        >>> errors = SpanFilter.with_status(SpanStatus.Error)
        >>> either = retries.or_(errors)
        >>> # Matches spans: name matches "retry.*" OR status is Error

        Complex nested filter:

        >>> # Find LLM spans that either errored or took too long
        >>> llm_filter = SpanFilter.by_name_pattern("llm.*")
        >>> error_filter = SpanFilter.with_status(SpanStatus.Error)
        >>> slow_filter = SpanFilter.with_duration(min_ms=10000)
        >>> combined = llm_filter.and_(error_filter.or_(slow_filter))

    Note:
        - Filters are immutable; and() and or() return new filter instances
        - Regex patterns use standard regex syntax
        - Duration is measured in milliseconds
        - Attribute values are internally wrapped for type safety
    """

    class ByName(SpanFilter):
        """Filter spans by exact name match."""

        name: str
        def __new__(cls, name: str) -> "SpanFilter.ByName": ...

    class ByNamePattern(SpanFilter):
        """Filter spans by regex name pattern."""

        pattern: str
        def __new__(cls, pattern: str) -> "SpanFilter.ByNamePattern": ...

    class WithAttribute(SpanFilter):
        """Filter spans with specific attribute key."""

        key: str
        def __new__(cls, key: str) -> "SpanFilter.WithAttribute": ...

    class WithAttributeValue(SpanFilter):
        """Filter spans with specific attribute key-value pair."""

        key: str
        value: Any
        def __new__(cls, key: str, value: Any) -> "SpanFilter.WithAttributeValue": ...

    class WithStatus(SpanFilter):
        """Filter spans by status code."""

        status: SpanStatus
        def __new__(cls, status: SpanStatus) -> "SpanFilter.WithStatus": ...

    class WithDuration(SpanFilter):
        """Filter spans with duration constraints."""

        min_ms: Optional[float]
        max_ms: Optional[float]
        def __new__(
            cls, min_ms: Optional[float] = None, max_ms: Optional[float] = None
        ) -> "SpanFilter.WithDuration": ...

    class Sequence(SpanFilter):
        """Match a sequence of span names in order."""

        names: List[str]
        def __new__(cls, names: List[str]) -> "SpanFilter.Sequence": ...

    class And(SpanFilter):
        """Combine multiple filters with AND logic."""

        filters: List["SpanFilter"]
        def __new__(cls, filters: List["SpanFilter"]) -> "SpanFilter.And": ...

    class Or(SpanFilter):
        """Combine multiple filters with OR logic."""

        filters: List["SpanFilter"]
        def __new__(cls, filters: List["SpanFilter"]) -> "SpanFilter.Or": ...

    @staticmethod
    def by_name(name: str) -> "SpanFilter.ByName":
        """Filter spans by exact name match.

        Args:
            name (str):
                Exact span name to match (case-sensitive).

        Returns:
            SpanFilter that matches spans with the specified name.
        """

    @staticmethod
    def by_name_pattern(pattern: str) -> "SpanFilter.ByNamePattern":
        """Filter spans by regex name pattern.

        Args:
            pattern (str):
                Regular expression pattern to match span names.

        Returns:
            SpanFilter that matches spans whose names match the pattern.
        """

    @staticmethod
    def with_attribute(key: str) -> "SpanFilter.WithAttribute":
        """Filter spans that have a specific attribute key.

        Args:
            key (str):
                Attribute key to check for existence.

        Returns:
            SpanFilter that matches spans with the specified attribute.
        """

    @staticmethod
    def with_attribute_value(key: str, value: "SerializedType") -> "SpanFilter.WithAttributeValue":
        """Filter spans that have a specific attribute key-value pair.

        Args:
            key (str):
                Attribute key to check.
            value (SerializedType):
                Attribute value to match (must be JSON-serializable).

        Returns:
            SpanFilter that matches spans with the specified key-value pair.
        """

    @staticmethod
    def with_status(status: SpanStatus) -> "SpanFilter.WithStatus":
        """Filter spans by execution status.

        Args:
            status (SpanStatus):
                SpanStatus to match (Ok, Error, or Unset).

        Returns:
            SpanFilter that matches spans with the specified status.
        """

    @staticmethod
    def with_duration(min_ms: Optional[float] = None, max_ms: Optional[float] = None) -> "SpanFilter.WithDuration":
        """Filter spans by duration constraints.

        Args:
            min_ms (Optional[float]):
                Optional minimum duration in milliseconds.
            max_ms (Optional[float]):
                Optional maximum duration in milliseconds.

        Returns:
            SpanFilter that matches spans within the duration range.
            If both are None, matches all spans.
        """

    @staticmethod
    def sequence(names: List[str]) -> "SpanFilter.Sequence":
        """Filter for spans appearing in specific order.

        Args:
            names (List[str]):
                List of span names that must appear in order.

        Returns:
            SpanFilter that matches the span sequence.
        """

    def and_(self, other: "SpanFilter") -> "SpanFilter":
        """Combine this filter with another using AND logic.

        Args:
            other (SpanFilter):
                Another SpanFilter to combine with.

        Returns:
            New SpanFilter matching spans that satisfy both conditions.
        """

    def or_(self, other: "SpanFilter") -> "SpanFilter":
        """Combine this filter with another using OR logic.

        Args:
            other (SpanFilter):
                Another SpanFilter to combine with.

        Returns:
            New SpanFilter matching spans that satisfy either condition.
        """

class TraceAssertion:
    """Assertion target for trace and span properties.

    Defines what aspect of a trace or its spans should be evaluated.
    TraceAssertion types fall into three categories:

    1. Span-level assertions: Evaluate properties of filtered spans
       (count, existence, attributes, duration, aggregations)

    2. Span collection assertions: Evaluate span sets and sequences
       (span_set for existence, span_sequence for ordering)

    3. Trace-level assertions: Evaluate entire trace properties
       (total duration, span count, error count, max depth)

    Each assertion type extracts a value that is then compared against
    an expected value using the operator specified in TraceAssertionTask.

    Examples:
        Check execution order of spans:

        >>> assertion = TraceAssertion.span_sequence([
        ...     "validate_input",
        ...     "process_data",
        ...     "generate_output"
        ... ])
        >>> # Use with SequenceMatches operator

        Check all required spans exist (order doesn't matter):

        >>> assertion = TraceAssertion.span_set([
        ...     "call_tool",
        ...     "run_agent",
        ...     "double_check"
        ... ])
        >>> # Use with ContainsAll operator

        Count spans matching a filter:

        >>> filter = SpanFilter.by_name("retry_operation")
        >>> assertion = TraceAssertion.span_count(filter)
        >>> # Use with LessThanOrEqual to limit retries

        Check if specific span exists:

        >>> filter = SpanFilter.by_name_pattern("llm.*")
        >>> assertion = TraceAssertion.span_exists(filter)
        >>> # Use with Equals(True) to verify LLM was called

        Get attribute value from span:

        >>> filter = SpanFilter.by_name("llm.generate")
        >>> assertion = TraceAssertion.span_attribute(filter, "model")
        >>> # Use with Equals("gpt-4") to verify model

        Get span duration:

        >>> filter = SpanFilter.by_name("database_query")
        >>> assertion = TraceAssertion.span_duration(filter)
        >>> # Use with LessThan to enforce SLA

        Aggregate numeric attribute across spans:

        >>> filter = SpanFilter.by_name_pattern("llm.*")
        >>> assertion = TraceAssertion.span_aggregation(
        ...     filter,
        ...     "token_count",
        ...     AggregationType.Sum
        ... )
        >>> # Use with LessThan to limit total tokens

        Check total trace duration:

        >>> assertion = TraceAssertion.trace_duration()
        >>> # Use with LessThan to enforce response time

        Count total spans in trace:

        >>> assertion = TraceAssertion.trace_span_count()
        >>> # Use with range operators to validate complexity

        Count error spans:

        >>> assertion = TraceAssertion.trace_error_count()
        >>> # Use with Equals(0) to ensure no errors

        Count unique services involved:

        >>> assertion = TraceAssertion.trace_service_count()
        >>> # Use to validate service boundaries

        Get maximum span depth:

        >>> assertion = TraceAssertion.trace_max_depth()
        >>> # Use to detect deep recursion

        Get trace-level attribute:

        >>> assertion = TraceAssertion.trace_attribute("user_id")
        >>> # Use to validate trace context

    Note:
        - Span assertions require SpanFilter to target specific spans
        - Aggregations only work on numeric attributes
        - Sequence matching preserves span order by start time
        - Trace-level assertions evaluate the entire trace without filtering
    """

    class SpanSequence(TraceAssertion):
        """Extracts a sequence of span names in order."""

        span_names: List[str]
        def __new__(cls, span_names: List[str]) -> "TraceAssertion.SpanSequence": ...

    class SpanSet(TraceAssertion):
        """Checks for existence of all specified span names."""

        span_names: List[str]
        def __new__(cls, span_names: List[str]) -> "TraceAssertion.SpanSet": ...

    class SpanCount(TraceAssertion):
        """Counts spans matching a filter."""

        filter: SpanFilter
        def __new__(cls, filter: SpanFilter) -> "TraceAssertion.SpanCount": ...

    class SpanExists(TraceAssertion):
        """Checks if any span matches a filter."""

        filter: SpanFilter
        def __new__(cls, filter: SpanFilter) -> "TraceAssertion.SpanExists": ...

    class SpanAttribute(TraceAssertion):
        """Extracts attribute value from span matching filter."""

        filter: SpanFilter
        attribute_key: str
        def __new__(cls, filter: SpanFilter, attribute_key: str) -> "TraceAssertion.SpanAttribute": ...

    class SpanDuration(TraceAssertion):
        """Extracts duration of span matching filter."""

        filter: SpanFilter
        def __new__(cls, filter: SpanFilter) -> "TraceAssertion.SpanDuration": ...

    class SpanAggregation(TraceAssertion):
        """Aggregates numeric attribute across filtered spans."""

        filter: SpanFilter
        attribute_key: str
        aggregation: AggregationType
        def __new__(
            cls, filter: SpanFilter, attribute_key: str, aggregation: AggregationType
        ) -> "TraceAssertion.SpanAggregation": ...

    class TraceAttribute(TraceAssertion):
        """Extracts trace-level attribute value."""

        attribute_key: str
        def __new__(cls, attribute_key: str) -> "TraceAssertion.TraceAttribute": ...

    class TraceDuration(TraceAssertion):
        """Get total duration of the entire trace."""

        def __new__(cls) -> "TraceAssertion.TraceDuration": ...

    class TraceSpanCount(TraceAssertion):
        """Count total spans in the trace."""

        def __new__(cls) -> "TraceAssertion.TraceSpanCount": ...

    class TraceErrorCount(TraceAssertion):
        """Count spans with errors in the trace."""

        def __new__(cls) -> "TraceAssertion.TraceErrorCount": ...

    class TraceServiceCount(TraceAssertion):
        """Count unique services in the trace."""

        def __new__(cls) -> "TraceAssertion.TraceServiceCount": ...

    class TraceMaxDepth(TraceAssertion):
        """Get maximum span depth in the trace."""

        def __new__(cls) -> "TraceAssertion.TraceMaxDepth": ...

    @staticmethod
    def span_sequence(span_names: List[str]) -> "TraceAssertion.SpanSequence":
        """Assert spans appear in specific order.

        Args:
            span_names (List[str]):
                List of span names that must appear sequentially.

        Returns:
            TraceAssertion that extracts the span sequence.
            Use with SequenceMatches operator.
        """

    @staticmethod
    def span_set(span_names: List[str]) -> "TraceAssertion.SpanSet":
        """Assert all specified spans exist (order independent).

        Args:
            span_names (List[str]):
                List of span names that must all be present.

        Returns:
            TraceAssertion that checks for span set membership.
            Use with ContainsAll operator.
        """

    @staticmethod
    def span_count(filter: SpanFilter) -> "TraceAssertion.SpanCount":
        """Count spans matching the filter.

        Args:
            filter (SpanFilter):
                SpanFilter defining which spans to count.

        Returns:
            TraceAssertion that extracts the span count.
            Use with numeric comparison operators.
        """

    @staticmethod
    def span_exists(filter: SpanFilter) -> "TraceAssertion.SpanExists":
        """Check if any span matches the filter.

        Args:
            filter (SpanFilter):
                SpanFilter defining which span to look for.

        Returns:
            TraceAssertion that extracts boolean existence.
            Use with Equals(True/False).
        """

    @staticmethod
    def span_attribute(filter: SpanFilter, attribute_key: str) -> "TraceAssertion.SpanAttribute":
        """Get attribute value from span matching filter.

        Args:
            filter (SpanFilter):
                SpanFilter to identify the span.
            attribute_key (str):
                Attribute key to extract.

        Returns:
            TraceAssertion that extracts the attribute value.
            Use with appropriate operators for the value type.
        """

    @staticmethod
    def span_duration(filter: SpanFilter) -> "TraceAssertion.SpanDuration":
        """Get duration of span matching filter.

        Args:
            filter (SpanFilter):
                SpanFilter to identify the span.

        Returns:
            TraceAssertion that extracts span duration in milliseconds.
            Use with numeric comparison operators.
        """

    @staticmethod
    def span_aggregation(
        filter: SpanFilter, attribute_key: str, aggregation: AggregationType
    ) -> "TraceAssertion.SpanAggregation":
        """Aggregate numeric attribute across filtered spans.

        Args:
            filter (SpanFilter):
                SpanFilter to identify spans.
            attribute_key (str):
                Numeric attribute to aggregate.
            aggregation (AggregationType):
                Defining how to aggregate.

        Returns:
            TraceAssertion that computes the aggregation.
            Use with numeric comparison operators.
        """

    @staticmethod
    def trace_duration() -> "TraceAssertion.TraceDuration":
        """Get total duration of the entire trace.

        Returns:
            TraceAssertion that extracts trace duration in milliseconds.
            Use with numeric comparison operators for SLA validation.
        """

    @staticmethod
    def trace_span_count() -> "TraceAssertion.TraceSpanCount":
        """Count total spans in the trace.

        Returns:
            TraceAssertion that extracts total span count.
            Use with numeric operators to validate trace complexity.
        """

    @staticmethod
    def trace_error_count() -> "TraceAssertion.TraceErrorCount":
        """Count spans with error status in the trace.

        Returns:
            TraceAssertion that counts error spans.
            Use with Equals(0) to ensure no errors occurred.
        """

    @staticmethod
    def trace_service_count() -> "TraceAssertion.TraceServiceCount":
        """Count unique services involved in the trace.

        Returns:
            TraceAssertion that counts distinct services.
            Use to validate service boundaries or detect sprawl.
        """

    @staticmethod
    def trace_max_depth() -> "TraceAssertion.TraceMaxDepth":
        """Get maximum nesting depth of span tree.

        Returns:
            TraceAssertion that extracts max span depth.
            Use to detect deep recursion or validate call hierarchy.
        """

    @staticmethod
    def trace_attribute(attribute_key: str) -> "TraceAssertion.TraceAttribute":
        """Get trace-level attribute value.

        Args:
            attribute_key (str):
                Attribute key from trace context.

        Returns:
            TraceAssertion that extracts the trace attribute.
            Use with appropriate operators for the value type.
        """

    @staticmethod
    def attribute_filter(key: str, task: "AttributeFilterTask", mode: "MultiResponseMode") -> "TraceAssertion":
        """Filter spans by attribute and apply assertion to collected spans.

        Args:
            key (str):
                Attribute key to filter spans.
            task (AttributeFilterTask):
                Assertion task to apply to the filtered spans.
            mode (MultiResponseMode):
                Mode to handle multiple spans matching the filter (e.g., apply to all, any).
        """

class TraceAssertionTask:
    """Trace-based evaluation task for behavioral assertions.

    Evaluates trace and span properties to validate execution behavior,
    performance characteristics, and service interactions. Unlike AssertionTask
    which operates on LLM responses, TraceAssertionTask analyzes distributed
    traces to ensure agents and services behave correctly.

    TraceAssertionTask is essential for:
        - Validating agent workflow execution order
        - Ensuring required services are called
        - Enforcing performance SLAs
        - Detecting error patterns
        - Verifying span attributes and metadata
        - Analyzing service dependencies

    Each task combines three components:
        1. TraceAssertion: What to measure (span count, duration, etc.)
        2. ComparisonOperator: How to compare (equals, greater than, etc.)
        3. Expected Value: What value to compare against

    Common Use Cases:
        - Workflow validation: Verify spans execute in correct order
        - Completeness checks: Ensure all required steps were executed
        - Performance monitoring: Enforce latency SLAs
        - Error detection: Validate error-free execution
        - Resource validation: Check correct models/services were used
        - Complexity bounds: Limit retry counts or recursion depth

    Examples:
        Verify agent execution order:

        >>> task = TraceAssertionTask(
        ...     id="verify_agent_workflow",
        ...     assertion=TraceAssertion.span_sequence([
        ...         "call_tool",
        ...         "run_agent",
        ...         "double_check"
        ...     ]),
        ...     operator=ComparisonOperator.SequenceMatches,
        ...     expected_value=True,
        ...     description="Verify correct agent execution order"
        ... )

        Ensure all required steps exist:

        >>> task = TraceAssertionTask(
        ...     id="verify_required_steps",
        ...     assertion=TraceAssertion.span_set([
        ...         "validate_input",
        ...         "process_data",
        ...         "generate_output"
        ...     ]),
        ...     operator=ComparisonOperator.ContainsAll,
        ...     expected_value=True,
        ...     description="Ensure all pipeline steps were executed"
        ... )

        Enforce total trace duration SLA:

        >>> task = TraceAssertionTask(
        ...     id="verify_performance",
        ...     assertion=TraceAssertion.trace_duration(),
        ...     operator=ComparisonOperator.LessThan,
        ...     expected_value=5000.0,  # 5 seconds in milliseconds
        ...     description="Ensure execution completes within 5 seconds"
        ... )

        Limit retry attempts:

        >>> filter = SpanFilter.by_name("retry_operation")
        >>> task = TraceAssertionTask(
        ...     id="verify_retry_limit",
        ...     assertion=TraceAssertion.span_count(filter),
        ...     operator=ComparisonOperator.LessThanOrEqual,
        ...     expected_value=3,
        ...     description="Ensure no more than 3 retries"
        ... )

        Verify correct model was used:

        >>> filter = SpanFilter.by_name("llm.generate")
        >>> task = TraceAssertionTask(
        ...     id="verify_model_used",
        ...     assertion=TraceAssertion.span_attribute(filter, "model"),
        ...     operator=ComparisonOperator.Equals,
        ...     expected_value="gpt-4",
        ...     description="Verify gpt-4 was used"
        ... )

        Ensure error-free execution:

        >>> task = TraceAssertionTask(
        ...     id="no_errors",
        ...     assertion=TraceAssertion.trace_error_count(),
        ...     operator=ComparisonOperator.Equals,
        ...     expected_value=0,
        ...     description="Verify no errors occurred"
        ... )

        Limit total token usage:

        >>> filter = SpanFilter.by_name_pattern("llm.*")
        >>> task = TraceAssertionTask(
        ...     id="token_budget",
        ...     assertion=TraceAssertion.span_aggregation(
        ...         filter,
        ...         "token_count",
        ...         AggregationType.Sum
        ...     ),
        ...     operator=ComparisonOperator.LessThan,
        ...     expected_value=10000,
        ...     description="Ensure total tokens under budget"
        ... )

        With dependencies:

        >>> task = TraceAssertionTask(
        ...     id="verify_database_performance",
        ...     assertion=TraceAssertion.span_duration(
        ...         SpanFilter.by_name("database_query")
        ...     ),
        ...     operator=ComparisonOperator.LessThan,
        ...     expected_value=100,  # 100ms
        ...     depends_on=["verify_agent_workflow"],
        ...     description="Verify database query performance after workflow validation"
        ... )

    Note:
        - Traces must be collected and available before evaluation
        - Span names and attributes depend on instrumentation
        - Duration is measured in milliseconds
        - Use dependencies to chain trace assertions with other tasks
        - Condition tasks can gate subsequent evaluations
    """

    def __init__(
        self,
        id: str,
        assertion: TraceAssertion,
        expected_value: Any,
        operator: ComparisonOperator,
        description: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        condition: bool = False,
    ):
        """Initialize a trace assertion task for behavioral validation.

        Args:
            id (str):
                Unique identifier for the task. Will be converted to lowercase.
                Used to reference this task in dependencies and results.
            assertion (TraceAssertion):
                TraceAssertion defining what to measure (span count, duration,
                attributes, etc.). Determines the value extracted from the trace.
            expected_value (Any):
                Expected value to compare against. Type depends on the assertion:
                - Numeric for counts, durations, aggregations
                - Boolean for existence checks
                - String/dict for attribute comparisons
                - List for sequence/set operations
            operator (ComparisonOperator):
                ComparisonOperator defining how to compare the extracted value
                against expected_value. Must be appropriate for the assertion type.
            description (Optional[str]):
                Optional human-readable description of what this assertion validates.
                Useful for understanding evaluation results.
            depends_on (Optional[List[str]]):
                Optional list of task IDs that must complete successfully before
                this task executes. Empty list if not provided.
            condition (bool):
                If True, this assertion acts as a condition for subsequent tasks.
                If the assertion fails, dependent tasks will be skipped and this
                task will be excluded from final results.

        Raises:
            TypeError: If expected_value is not JSON-serializable or if operator
                is not a valid ComparisonOperator.
        """

    @property
    def id(self) -> str:
        """Unique task identifier (lowercase)."""

    @id.setter
    def id(self, id: str) -> None:
        """Set task identifier (will be converted to lowercase)."""

    @property
    def assertion(self) -> TraceAssertion:
        """TraceAssertion defining what to measure in the trace."""

    @assertion.setter
    def assertion(self, assertion: TraceAssertion) -> None:
        """Set trace assertion target.

        Args:
            assertion (TraceAssertion):
                TraceAssertion defining what to measure.
        """

    @property
    def operator(self) -> ComparisonOperator:
        """Comparison operator for the assertion."""

    @operator.setter
    def operator(self, operator: ComparisonOperator) -> None:
        """Set comparison operator.

        Args:
            operator (ComparisonOperator):
                ComparisonOperator defining how to compare values.
        """

    @property
    def expected_value(self) -> Any:
        """Expected value for comparison.

        Returns:
            The expected value as a Python object (deserialized from internal
            JSON representation).
        """

    @property
    def description(self) -> Optional[str]:
        """Human-readable description of the assertion."""

    @description.setter
    def description(self, description: Optional[str]) -> None:
        """Set assertion description.

        Args:
            description (Optional[str]):
                Human-readable description of the assertion.
        """

    @property
    def depends_on(self) -> List[str]:
        """List of task IDs this task depends on."""

    @depends_on.setter
    def depends_on(self, depends_on: List[str]) -> None:
        """Set task dependencies.

        Args:
            depends_on (List[str]):
                List of task IDs that must complete before this task.
        """

    @property
    def condition(self) -> bool:
        """Indicates if this task is a condition for subsequent tasks."""

    @condition.setter
    def condition(self, condition: bool) -> None:
        """Set whether this task is a condition for subsequent tasks."""

    @property
    def task_type(self) -> EvaluationTaskType:
        """The type of this evaluation task (TraceAssertion)."""

    def __str__(self) -> str:
        """Return string representation of the trace assertion task."""

class TokenUsage:
    """Token usage statistics for an LLM response.

    Attributes:
        input_tokens (Optional[int]): Number of input/prompt tokens.
        output_tokens (Optional[int]): Number of output/completion tokens.
        total_tokens (Optional[int]): Total tokens consumed.
    """

    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]

    def __new__(
        cls,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
    ) -> "TokenUsage": ...
    def __str__(self) -> str: ...

class AgentAssertion:
    """Assertion target for agent tool calls and response properties.

    Defines what aspect of an agent interaction should be evaluated.
    AgentAssertion variants fall into two categories:

    1. Tool assertions: Evaluate tool call behavior
       (tool_called, tool_not_called, tool_called_with_args, tool_call_sequence,
        tool_call_count, tool_argument, tool_result)

    2. Response assertions: Evaluate LLM response properties
       (response_content, response_model, response_finish_reason,
        response_input_tokens, response_output_tokens, response_total_tokens,
        response_field)

    Each assertion variant extracts a value from the agent context that is then
    compared against an expected value using the operator in AgentAssertionTask.

    Examples:
        Check that a specific tool was called:

        >>> assertion = AgentAssertion.tool_called("search_web")
        >>> # Use with Equals(True)

        Check that a tool was called with specific arguments:

        >>> assertion = AgentAssertion.tool_called_with_args("search_web", {"query": "weather"})
        >>> # Use with Equals(True)

        Check tool call order:

        >>> assertion = AgentAssertion.tool_call_sequence(["search_web", "summarize"])
        >>> # Use with SequenceMatches operator

        Inspect a specific field in the response:

        >>> assertion = AgentAssertion.response_field("choices.0.message.content")
        >>> # Use with Contains operator
    """

    class ToolCalled:
        """Check if a specific tool was called."""

        name: str

    class ToolNotCalled:
        """Check if a specific tool was NOT called."""

        name: str

    class ToolCalledWithArgs:
        """Check if a tool was called with specific arguments (partial match)."""

        name: str
        arguments: object  # PyValueWrapper is internal, exposed as object

    class ToolCallSequence:
        """Check if tools were called in exact sequence."""

        names: List[str]

    class ToolCallCount:
        """Count tool calls, optionally filtered by name."""

        name: Optional[str]

    class ToolArgument:
        """Extract a specific argument value from a tool call."""

        name: str
        argument_key: str

    class ToolResult:
        """Extract the result returned by a tool call."""

        name: str

    class ResponseContent:
        """Get the text content of the response."""

    class ResponseModel:
        """Get the model name used in the response."""

    class ResponseFinishReason:
        """Get the finish/stop reason of the response."""

    class ResponseInputTokens:
        """Get the input token count of the response."""

    class ResponseOutputTokens:
        """Get the output token count of the response."""

    class ResponseTotalTokens:
        """Get the total token count of the response."""

    class ResponseField:
        """Extract a field from the raw response via dot-notation path."""

        path: str

    def __str__(self) -> str: ...
    @staticmethod
    def tool_called(name: str) -> "AgentAssertion":
        """Assert that a tool with the given name was called.

        Args:
            name (str):
                Name of the tool to check.

        Returns:
            AgentAssertion that checks tool call existence.
        """

    @staticmethod
    def tool_not_called(name: str) -> "AgentAssertion":
        """Assert that a tool with the given name was NOT called.

        Args:
            name (str):
                Name of the tool to check.

        Returns:
            AgentAssertion that checks tool call absence.
        """

    @staticmethod
    def tool_called_with_args(name: str, arguments: Dict[str, Any]) -> "AgentAssertion":
        """Assert that a tool was called with specific arguments (partial match).

        Args:
            name (str):
                Name of the tool.
            arguments (Dict[str, Any]):
                Expected arguments dict (partial match).

        Returns:
            AgentAssertion that checks tool call arguments.
        """

    @staticmethod
    def tool_call_sequence(names: List[str]) -> "AgentAssertion":
        """Assert that tools were called in the given exact sequence.

        Args:
            names (List[str]):
                Ordered list of tool names.

        Returns:
            AgentAssertion that checks the tool call sequence.
        """

    @staticmethod
    def tool_call_count(name: Optional[str] = None) -> "AgentAssertion":
        """Extract the number of times a tool (or any tool) was called.

        Args:
            name (Optional[str]):
                Tool name to count, or None to count all tool calls.

        Returns:
            AgentAssertion that extracts a call count for comparison.
        """

    @staticmethod
    def tool_argument(name: str, argument_key: str) -> "AgentAssertion":
        """Extract a specific argument value from a tool call.

        Args:
            name (str):
                Name of the tool.
            argument_key (str):
                Key of the argument to extract.

        Returns:
            AgentAssertion that extracts the argument value.
        """

    @staticmethod
    def tool_result(name: str) -> "AgentAssertion":
        """Extract the result returned by a tool call.

        Args:
            name (str):
                Name of the tool.

        Returns:
            AgentAssertion that extracts the tool result.
        """

    @staticmethod
    def response_content() -> "AgentAssertion":
        """Extract the text content of the agent response.

        Returns:
            AgentAssertion that extracts response content.
        """

    @staticmethod
    def response_model() -> "AgentAssertion":
        """Extract the model identifier used in the agent response.

        Returns:
            AgentAssertion that extracts the response model name.
        """

    @staticmethod
    def response_finish_reason() -> "AgentAssertion":
        """Extract the finish reason of the agent response.

        Returns:
            AgentAssertion that extracts the finish reason.
        """

    @staticmethod
    def response_input_tokens() -> "AgentAssertion":
        """Extract the number of input tokens from the agent response.

        Returns:
            AgentAssertion that extracts input token count.
        """

    @staticmethod
    def response_output_tokens() -> "AgentAssertion":
        """Extract the number of output tokens from the agent response.

        Returns:
            AgentAssertion that extracts output token count.
        """

    @staticmethod
    def response_total_tokens() -> "AgentAssertion":
        """Extract the total number of tokens from the agent response.

        Returns:
            AgentAssertion that extracts total token count.
        """

    @staticmethod
    def response_field(path: str) -> "AgentAssertion":
        """Extract an arbitrary field from the raw response using dot-notation.

        Args:
            path (str):
                Dot-notation path into the response object
                (e.g. "choices[0].message.content").

        Returns:
            AgentAssertion that extracts the response field value.
        """

class AgentAssertionTask:
    """Agent-based evaluation task for behavioral assertions.

    Evaluates agent tool calls and response properties to validate execution
    behavior against expected values. Each task defines an assertion target
    (AgentAssertion), a comparison operator, and an expected value.

    Args:
        id (str):
            Unique identifier for this task (converted to lowercase).
        assertion (AgentAssertion):
            AgentAssertion defining what to measure in the agent interaction.
        expected_value (Any):
            The value to compare against the extracted assertion value.
            Must be JSON-serializable.
        operator (ComparisonOperator):
            How to compare the extracted value against expected_value.
        description (Optional[str]):
            Human-readable description of what this task checks.
        depends_on (Optional[List[str]]):
            Task IDs whose outputs this task may reference.
        condition (Optional[bool]):
            If True, this task acts as a gate — downstream tasks are
            skipped if this task fails.

    Examples:
        Check that a tool was called:

        >>> task = AgentAssertionTask(
        ...     id="tool_was_called",
        ...     assertion=AgentAssertion.tool_called("search_web"),
        ...     expected_value=True,
        ...     operator=ComparisonOperator.Equals,
        ... )

        Count total tool calls:

        >>> task = AgentAssertionTask(
        ...     id="tool_call_count",
        ...     assertion=AgentAssertion.tool_call_count(),
        ...     expected_value=3,
        ...     operator=ComparisonOperator.LessThanOrEqual,
        ... )
    """

    def __init__(
        self,
        id: str,
        assertion: AgentAssertion,
        expected_value: Any,
        operator: ComparisonOperator,
        description: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        condition: Optional[bool] = None,
        provider: Optional[Any] = None,
        context_path: Optional[str] = None,
    ) -> None:
        """Create an AgentAssertionTask.

        Args:
            id (str):
                Unique task identifier (converted to lowercase).
            assertion (AgentAssertion):
                AgentAssertion defining what to measure.
            expected_value (Any):
                Expected value for comparison. Must be JSON-serializable.
            operator (ComparisonOperator):
                Comparison operator for the assertion.
            description (Optional[str]):
                Human-readable description of the assertion.
            depends_on (Optional[List[str]]):
                Task IDs this task depends on.
            condition (Optional[bool]):
                If True, failed task skips subsequent tasks.
            provider (Optional[Provider]):
                Optional LLM provider hint (e.g. Provider.GoogleAdk) for
                accurate response parsing.
            context_path (Optional[str]):
                Dot-notation path to extract a sub-field from the context
                before evaluation (e.g. ``"response"``).

        Raises:
            TypeError: If expected_value is not JSON-serializable or if
                operator is not a valid ComparisonOperator.
        """

    @property
    def id(self) -> str:
        """Unique task identifier (lowercase)."""

    @id.setter
    def id(self, id: str) -> None:
        """Set task identifier (will be converted to lowercase)."""

    @property
    def assertion(self) -> AgentAssertion:
        """AgentAssertion defining what to measure in the agent interaction."""

    @assertion.setter
    def assertion(self, assertion: AgentAssertion) -> None:
        """Set agent assertion target.

        Args:
            assertion (AgentAssertion):
                AgentAssertion defining what to measure.
        """

    @property
    def operator(self) -> ComparisonOperator:
        """Comparison operator for the assertion."""

    @operator.setter
    def operator(self, operator: ComparisonOperator) -> None:
        """Set comparison operator.

        Args:
            operator (ComparisonOperator):
                ComparisonOperator defining how to compare values.
        """

    @property
    def expected_value(self) -> Any:
        """Expected value for comparison.

        Returns:
            The expected value as a Python object (deserialized from internal
            JSON representation).
        """

    @property
    def description(self) -> Optional[str]:
        """Human-readable description of the assertion."""

    @description.setter
    def description(self, description: Optional[str]) -> None:
        """Set assertion description.

        Args:
            description (Optional[str]):
                Human-readable description of the assertion.
        """

    @property
    def depends_on(self) -> List[str]:
        """List of task IDs this task depends on."""

    @depends_on.setter
    def depends_on(self, depends_on: List[str]) -> None:
        """Set task dependencies.

        Args:
            depends_on (List[str]):
                List of task IDs that must complete before this task.
        """

    @property
    def condition(self) -> bool:
        """Indicates if this task is a condition for subsequent tasks."""

    @condition.setter
    def condition(self, condition: bool) -> None:
        """Set whether this task is a condition for subsequent tasks."""

    @property
    def task_type(self) -> EvaluationTaskType:
        """The type of this evaluation task (AgentAssertion)."""

    @property
    def result(self) -> Optional[AssertionResult]:
        """Assertion result after task execution, or None if not yet run."""

    @property
    def provider(self) -> Optional[Any]:
        """Optional LLM provider hint for response parsing."""

    @provider.setter
    def provider(self, provider: Optional[Any]) -> None:
        """Set the LLM provider hint."""

    def __str__(self) -> str:
        """Return string representation of the agent assertion task."""

    def model_dump_json(self) -> str:
        """Serialize the task to a JSON string."""

class MultiResponseMode:
    """Mode for aggregating assertion results across multiple attribute values.

    When a span attribute contains multiple values (e.g. a list of responses),
    ``MultiResponseMode`` controls whether *any* or *all* of those values must
    satisfy the inner task to count as a pass.

    Variants:
        Any: At least one value must pass the inner task.
        All: Every value must pass the inner task.

    Examples:
        >>> mode = MultiResponseMode.Any
        >>> mode = MultiResponseMode.All
    """

    Any: "MultiResponseMode"
    All: "MultiResponseMode"

class AttributeFilterTask:
    """Inner task to run on each value extracted from a span attribute.

    ``AttributeFilterTask`` is the sub-task embedded inside a
    ``TraceAssertion.attribute_filter`` call.  It controls *how* each
    extracted attribute value is evaluated:

    - ``Assertion``: run a deterministic :class:`AssertionTask` directly on
      the raw extracted value.
    - ``AgentAssertion``: parse the value through ``AgentContextBuilder``
      (to reconstruct tool-call / response structure) and then evaluate with
      an :class:`AgentAssertionTask`.

    Use the static factory methods rather than constructing variants directly.

    Examples:
        Deterministic check on a raw attribute value:

        >>> task = AttributeFilterTask.assertion(
        ...     AssertionTask(
        ...         id="has_parts",
        ...         context_path="content.parts",
        ...         operator=ComparisonOperator.HasLengthGreaterThan,
        ...         expected_value=0,
        ...     )
        ... )

        Agent-level check (tool call) on a JSON-encoded response attribute:

        >>> task = AttributeFilterTask.agent_assertion(
        ...     AgentAssertionTask(
        ...         id="tool_was_called",
        ...         assertion=AgentAssertion.tool_called("transfer_to_agent"),
        ...         expected_value=True,
        ...         operator=ComparisonOperator.Equals,
        ...     )
        ... )
    """

    @staticmethod
    def assertion(task: AssertionTask) -> "AttributeFilterTask":
        """Create an ``Assertion`` variant wrapping *task*.

        Args:
            task (AssertionTask): The deterministic assertion to run on each
                extracted attribute value.

        Returns:
            AttributeFilterTask: An ``Assertion`` variant.
        """

    @staticmethod
    def agent_assertion(task: AgentAssertionTask) -> "AttributeFilterTask":
        """Create an ``AgentAssertion`` variant wrapping *task*.

        Args:
            task (AgentAssertionTask): The agent assertion to run after
                parsing the attribute value through ``AgentContextBuilder``.

        Returns:
            AttributeFilterTask: An ``AgentAssertion`` variant.
        """

class AssertionResult:
    @property
    def passed(self) -> bool: ...
    @property
    def actual(self) -> Any: ...
    @property
    def expected(self) -> Any: ...
    @property
    def message(self) -> str: ...
    def __str__(self): ...

class AssertionResults:
    @property
    def results(self) -> Dict[str, AssertionResult]: ...
    def __str__(self): ...
    def __getitem__(self, key: str) -> AssertionResult: ...

def execute_agent_assertion_tasks(tasks: List[AgentAssertionTask], context: Any) -> AssertionResults:
    """Execute agent assertion tasks against a provided request context.

    Args:
        tasks (List[AgentAssertionTask]):
            List of AgentAssertionTask to evaluate.
        context (Any):
            Python object representing the agent request/response context.
            Typically the raw response object from your LLM provider.

    Returns:
        AssertionResults containing results for each agent assertion task.

    Raises:
        ValueError: If tasks list is empty or context cannot be deserialized.
    """

def execute_trace_assertion_tasks(tasks: List[TraceAssertionTask], spans: List[TraceSpan]) -> AssertionResults:
    """Execute trace assertion tasks against provided spans.

    Args:
        tasks (List[TraceAssertionTask]):
            List of TraceAssertionTask to evaluate.
        spans (List[TraceSpan]):
            List of TraceSpan representing the collected trace data.

    Returns:
        AssertionResults containing results for each trace assertion task.

    Raises:
        ValueError: If tasks list is empty or spans are not provided.
    """

class TaskSummary:
    """Per-task pass/fail summary within a scenario result.

    Attributes:
        task_id (str): The task identifier.
        passed (bool): Whether the task passed.
        value (float): Numeric value (1.0 if passed, 0.0 if failed).
    """

    @property
    def task_id(self) -> str:
        """The task identifier."""

    @property
    def passed(self) -> bool:
        """Whether the task passed."""

    @property
    def value(self) -> float:
        """Numeric value (1.0 if passed, 0.0 if failed)."""

    def __str__(self) -> str:
        """Return a pretty-printed JSON string representation."""

class EvalMetrics:
    """Aggregate evaluation metrics across all scenarios and sub-agents.

    Produced by ``ScenarioEvalResults`` after a full offline evaluation run.
    Summarises both the holistic sub-agent pass rates and the per-scenario
    pass/fail counts.

    Attributes:
        overall_pass_rate (float):
            Average of output quality and internal workflow pass rates (0–1).
        dataset_pass_rates (Dict[str, float]):
            Per-alias workflow pass rate (0–1), keyed by alias name.
        scenario_pass_rate (float):
            Agent output matched expected results (0–1).
        workflow_pass_rate (float):
            Internal agent checks passed, averaged across aliases (0–1).
            Only present when at least one alias has workflow data.
        total_scenarios (int):
            Total number of scenarios evaluated.
        passed_scenarios (int):
            Number of scenarios where output matched expectations.
        scenario_task_pass_rates (Dict[str, Dict[str, float]]):
            Per-scenario, per-task pass rates. Maps scenario_id → task_id → pass_rate.
    """

    @property
    def overall_pass_rate(self) -> float:
        """Average of output quality and internal workflow pass rates (0–1)."""

    @property
    def dataset_pass_rates(self) -> Dict[str, float]:
        """Per-alias workflow pass rate (0–1), keyed by alias name."""

    @property
    def scenario_pass_rate(self) -> float:
        """Agent output matched expected results (0–1)."""

    @property
    def workflow_pass_rate(self) -> float:
        """Internal agent checks passed, averaged across aliases (0–1)."""

    @property
    def total_scenarios(self) -> int:
        """Total number of scenarios evaluated."""

    @property
    def passed_scenarios(self) -> int:
        """Number of scenarios where output matched expectations."""

    @property
    def scenario_task_pass_rates(self) -> Dict[str, Dict[str, float]]:
        """Per-scenario, per-task pass rates."""

    def __str__(self) -> str:
        """Return a pretty-printed JSON string representation."""

    def as_table(self) -> None:
        """Print an aggregate metrics summary table to stdout."""

class ScenarioResult:
    """Evaluation outcome for a single scenario.

    Contains the per-scenario task results alongside high-level pass/fail
    metadata.

    Attributes:
        scenario_id (str):
            Unique identifier of the evaluated scenario.
        initial_query (str):
            The opening query that was sent to the agent.
        eval_results (EvalResults):
            Full task-level evaluation results for this scenario.
        passed (bool):
            ``True`` when every task in this scenario passed.
        pass_rate (float):
            Fraction of tasks that passed (0–1).
        task_results (List[TaskSummary]):
            Per-task pass/fail summaries for this scenario.
    """

    @property
    def scenario_id(self) -> str:
        """Unique identifier of the evaluated scenario."""

    @property
    def initial_query(self) -> str:
        """The opening query sent to the agent."""

    @property
    def eval_results(self) -> "EvalResults":
        """Full task-level evaluation results for this scenario."""

    @property
    def passed(self) -> bool:
        """True when every task in this scenario passed."""

    @property
    def pass_rate(self) -> float:
        """Fraction of tasks that passed (0–1)."""

    @property
    def task_results(self) -> List["TaskSummary"]:
        """Per-task pass/fail summaries for this scenario."""

    def __str__(self) -> str:
        """Return a pretty-printed JSON string representation."""

class ScenarioDelta:
    """Pass/fail change record for a single scenario between two evaluation runs.

    Produced by ``ScenarioEvalResults.compare_to()``. Records whether a
    scenario's outcome changed (regressed or improved) relative to a baseline.

    Attributes:
        scenario_id (str):
            Unique identifier of the scenario.
        initial_query (str):
            The opening query for this scenario.
        baseline_passed (bool):
            Whether the scenario passed in the baseline run.
        comparison_passed (bool):
            Whether the scenario passed in the current run.
        baseline_pass_rate (float):
            Task pass rate (0–1) in the baseline run.
        comparison_pass_rate (float):
            Task pass rate (0–1) in the current run.
        status_changed (bool):
            ``True`` when ``baseline_passed != comparison_passed``.
    """

    @property
    def scenario_id(self) -> str:
        """Unique identifier of the scenario."""

    @property
    def initial_query(self) -> str:
        """The opening query for this scenario."""

    @property
    def baseline_passed(self) -> bool:
        """Whether the scenario passed in the baseline run."""

    @property
    def comparison_passed(self) -> bool:
        """Whether the scenario passed in the current run."""

    @property
    def baseline_pass_rate(self) -> float:
        """Task pass rate (0–1) in the baseline run."""

    @property
    def comparison_pass_rate(self) -> float:
        """Task pass rate (0–1) in the current run."""

    @property
    def status_changed(self) -> bool:
        """True when the pass/fail outcome changed between runs."""

    def __str__(self) -> str:
        """Return a pretty-printed JSON string representation."""

class ScenarioComparisonResults:
    """Regression comparison output between two ``ScenarioEvalResults`` runs.

    Produced by ``ScenarioEvalResults.compare_to()``. Surfaces both per-alias
    sub-agent regressions and individual scenario-level changes.

    Attributes:
        dataset_comparisons (Dict[str, ComparisonResults]):
            Per-alias comparison results, keyed by alias name.
        scenario_deltas (List[ScenarioDelta]):
            Per-scenario pass/fail change records.
        baseline_overall_pass_rate (float):
            Overall pass rate from the baseline run (0–1).
        comparison_overall_pass_rate (float):
            Overall pass rate from the current run (0–1).
        regressed (bool):
            ``True`` when at least one alias regressed beyond the threshold.
        improved_aliases (List[str]):
            Aliases that improved relative to the baseline.
        regressed_aliases (List[str]):
            Aliases that regressed relative to the baseline.

    Examples:
        Compare current results to a saved baseline:

        >>> baseline = ScenarioEvalResults.load("baseline.json")
        >>> comparison = current_results.compare_to(baseline, regression_threshold=0.05)
        >>> comparison.as_table()
        >>> if comparison.regressed:
        ...     print(f"Regressions: {comparison.regressed_aliases}")
    """

    @property
    def dataset_comparisons(self) -> Dict[str, "ComparisonResults"]:
        """Per-alias comparison results, keyed by alias name."""

    @property
    def scenario_deltas(self) -> List[ScenarioDelta]:
        """Per-scenario pass/fail change records."""

    @property
    def baseline_overall_pass_rate(self) -> float:
        """Overall pass rate from the baseline run (0–1)."""

    @property
    def comparison_overall_pass_rate(self) -> float:
        """Overall pass rate from the current run (0–1)."""

    @property
    def regressed(self) -> bool:
        """True when at least one alias regressed beyond the threshold."""

    @property
    def improved_aliases(self) -> List[str]:
        """Aliases that improved relative to the baseline."""

    @property
    def regressed_aliases(self) -> List[str]:
        """Aliases that regressed relative to the baseline."""

    @property
    def new_aliases(self) -> List[str]:
        """Aliases present in the current run but not in the baseline."""

    @property
    def removed_aliases(self) -> List[str]:
        """Aliases present in the baseline but not in the current run."""

    @property
    def new_scenarios(self) -> List[str]:
        """Scenario IDs present in the current run but not in the baseline."""

    @property
    def removed_scenarios(self) -> List[str]:
        """Scenario IDs present in the baseline but not in the current run."""

    @property
    def baseline_alias_pass_rates(self) -> Dict[str, float]:
        """Per-alias pass rates from the baseline run."""

    @property
    def comparison_alias_pass_rates(self) -> Dict[str, float]:
        """Per-alias pass rates from the current run."""

    def __str__(self) -> str:
        """Return a pretty-printed JSON string representation."""

    def model_dump_json(self) -> str:
        """Serialize the comparison results to a JSON string."""

    @staticmethod
    def model_validate_json(json_string: str) -> "ScenarioComparisonResults":
        """Deserialize comparison results from a JSON string.

        Args:
            json_string (str): JSON string produced by ``model_dump_json()``.

        Raises:
            RuntimeError: If the JSON is invalid or cannot be deserialized.
        """

    def save(self, path: str) -> None:
        """Serialize and write comparison results to a JSON file.

        Args:
            path (str): Filesystem path to write the JSON file.

        Raises:
            RuntimeError: If the file cannot be written.
        """

    @staticmethod
    def load(path: str) -> "ScenarioComparisonResults":
        """Load comparison results from a JSON file written by ``save()``.

        Args:
            path (str): Filesystem path of the JSON file.

        Raises:
            RuntimeError: If the file cannot be read or parsed.
        """

    def as_table(self) -> None:
        """Print a regression summary table to stdout.

        Shows sub-agent pass rate comparison, all scenario deltas with
        pass rate changes, new/removed scenarios, and an overall summary.
        """

class ScenarioEvalResults:
    """Complete output of an offline agent evaluation run.

    Contains per-alias holistic results (all scenarios flattened per sub-agent),
    per-scenario results, and aggregate metrics.

    Produced by ``EvalScenarios.evaluate()``.

    Attributes:
        dataset_results (Dict[str, EvalResults]):
            Per-alias holistic evaluation results across all scenarios.
        scenario_results (List[ScenarioResult]):
            Per-scenario evaluation results.
        metrics (EvalMetrics):
            Aggregate metrics (overall pass rate, scenario pass rate, counts).

    Examples:
        Save and reload results for regression testing:

        >>> results.save("eval_run_v1.json")
        >>> baseline = ScenarioEvalResults.load("eval_run_v1.json")
        >>> comparison = results.compare_to(baseline)
        >>> comparison.as_table()

        Inspect a specific scenario:

        >>> detail = results.get_scenario_detail("scenario-uuid-here")
        >>> print(detail.pass_rate)
    """

    @property
    def dataset_results(self) -> Dict[str, "EvalResults"]:
        """Per-alias holistic evaluation results across all scenarios."""

    @property
    def scenario_results(self) -> List[ScenarioResult]:
        """Per-scenario evaluation results."""

    @property
    def metrics(self) -> EvalMetrics:
        """Aggregate metrics (overall pass rate, scenario pass rate, counts)."""

    def __str__(self) -> str:
        """Return a pretty-printed JSON string representation."""

    def model_dump_json(self) -> str:
        """Serialize the results to a JSON string."""

    @staticmethod
    def model_validate_json(json_string: str) -> "ScenarioEvalResults":
        """Deserialize results from a JSON string.

        Args:
            json_string (str): JSON string produced by ``model_dump_json()``.

        Raises:
            RuntimeError: If the JSON is invalid or cannot be deserialized.
        """

    def save(self, path: str) -> None:
        """Serialize and write results to a JSON file.

        Args:
            path (str): Filesystem path to write the JSON file.

        Raises:
            RuntimeError: If the file cannot be written.
        """

    @staticmethod
    def load(path: str) -> "ScenarioEvalResults":
        """Load results from a JSON file written by ``save()``.

        Args:
            path (str): Filesystem path of the JSON file.

        Raises:
            RuntimeError: If the file cannot be read or parsed.
        """

    def get_scenario_detail(self, scenario_id: str) -> ScenarioResult:
        """Return the result for a specific scenario by ID.

        Args:
            scenario_id (str): The scenario's unique identifier.

        Raises:
            RuntimeError: If no scenario with that ID exists in the results.
        """

    def compare_to(
        self,
        baseline: "ScenarioEvalResults",
        regression_threshold: float = 0.05,
    ) -> ScenarioComparisonResults:
        """Compare these results against a baseline run for regression detection.

        Performs per-alias sub-agent comparison using ``ComparisonResults`` and
        per-scenario pass/fail delta tracking.

        Args:
            baseline (ScenarioEvalResults):
                The baseline evaluation results to compare against.
            regression_threshold (float):
                Minimum pass-rate drop (0–1) to flag as a regression.
                Defaults to 0.05 (5 percentage points).

        Returns:
            ScenarioComparisonResults with per-alias and per-scenario deltas.

        Raises:
            RuntimeError: If comparison computation fails.
        """

    def as_table(self, show_workflow: bool = False) -> None:
        """Print a full evaluation summary (metrics + scenario table) to stdout.

        Args:
            show_workflow: If True, also print per-dataset workflow summary tables.
        """

class EvalScenario:
    """A single test case in an offline agent evaluation run.

    Scenarios drive ``EvalScenarios`` (the orchestrator). At minimum, supply an
    ``initial_query``. Everything else is optional.

    Task attachment:
        Use ``tasks`` to attach scenario-level evaluation tasks (any of the four
        task types: ``AssertionTask``, ``LLMJudgeTask``, ``AgentAssertionTask``,
        ``TraceAssertionTask``). These are evaluated against the agent's **final
        response** for this specific scenario.

    Multi-turn scenarios:
        Populate ``predefined_turns`` with follow-up queries (executed in order
        after ``initial_query``). Leave empty for single-turn evaluation.

    ReAct / simulated-user scenarios:
        ``simulated_user_persona`` and ``termination_signal`` are placeholder
        fields for future ReAct support. Setting them has no effect in the
        current implementation.

    Args:
        initial_query (str):
            The opening query or prompt sent to the agent.
        tasks (Optional[List[AssertionTask | LLMJudgeTask | AgentAssertionTask | TraceAssertionTask]]):
            Scenario-level evaluation tasks. Evaluated against the agent's final
            response for this scenario.
        id (Optional[str]):
            Unique identifier for this scenario. Auto-generated (UUID7) if not
            provided.
        expected_outcome (Optional[str]):
            Ground-truth or reference answer. Available as ``${expected_outcome}``
            in task template variables.
        predefined_turns (Optional[List[str]]):
            Scripted follow-up queries for multi-turn scenarios (executed in
            order after ``initial_query``).
        simulated_user_persona (Optional[str]):
            Placeholder for future ReAct simulated-user support. No effect now.
        termination_signal (Optional[str]):
            Placeholder for future ReAct termination detection. No effect now.
        max_turns (int):
            Maximum number of turns for multi-turn evaluation. Defaults to 10.
        metadata (Optional[Dict[str, Any]]):
            Arbitrary key-value metadata attached to this scenario.

    Examples:
        Simple single-turn scenario:

        >>> scenario = EvalScenario(
        ...     initial_query="What is the capital of France?",
        ...     expected_outcome="Paris",
        ... )

        With assertion tasks:

        >>> from scouter.evaluate import AssertionTask, ComparisonOperator
        >>> task = AssertionTask(
        ...     id="check_response",
        ...     context_path="response",
        ...     operator=ComparisonOperator.Contains,
        ...     expected_value="Paris",
        ... )
        >>> scenario = EvalScenario(
        ...     initial_query="What is the capital of France?",
        ...     expected_outcome="Paris",
        ...     tasks=[task],
        ... )

        Multi-turn scenario:

        >>> scenario = EvalScenario(
        ...     initial_query="Plan a pasta dinner for 4 people.",
        ...     predefined_turns=["Make it vegetarian.", "Add a dessert option."],
        ...     expected_outcome="A complete vegetarian dinner plan.",
        ... )
    """

    def __init__(
        self,
        initial_query: str,
        tasks: Optional[List[Any]] = None,
        id: Optional[str] = None,
        expected_outcome: Optional[str] = None,
        predefined_turns: Optional[List[str]] = None,
        simulated_user_persona: Optional[str] = None,
        termination_signal: Optional[str] = None,
        max_turns: int = 10,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None: ...
    def __str__(self) -> str:
        """Return a pretty-printed JSON string representation."""

    def model_dump_json(self) -> str:
        """Serialize the scenario to a JSON string."""

    def model_dump(self) -> Dict[str, Any]:
        """Serialize the scenario to a Python dictionary."""

    def is_multi_turn(self) -> bool:
        """Return True when ``predefined_turns`` is non-empty."""

    def is_reactive(self) -> bool:
        """Return True when ``simulated_user_persona`` is set (ReAct placeholder)."""

    @property
    def id(self) -> str:
        """Unique scenario identifier (UUID7 by default)."""

    @id.setter
    def id(self, value: str) -> None: ...
    @property
    def initial_query(self) -> str:
        """The opening query sent to the agent."""

    @initial_query.setter
    def initial_query(self, value: str) -> None: ...
    @property
    def predefined_turns(self) -> List[str]:
        """Scripted follow-up queries for multi-turn scenarios."""

    @predefined_turns.setter
    def predefined_turns(self, value: List[str]) -> None: ...
    @property
    def simulated_user_persona(self) -> Optional[str]:
        """Simulated user persona string (ReAct placeholder)."""

    @simulated_user_persona.setter
    def simulated_user_persona(self, value: Optional[str]) -> None: ...
    @property
    def termination_signal(self) -> Optional[str]:
        """Termination signal string (ReAct placeholder)."""

    @termination_signal.setter
    def termination_signal(self, value: Optional[str]) -> None: ...
    @property
    def max_turns(self) -> int:
        """Maximum number of turns for multi-turn evaluation."""

    @max_turns.setter
    def max_turns(self, value: int) -> None: ...
    @property
    def expected_outcome(self) -> Optional[str]:
        """Ground-truth or reference answer for this scenario."""

    @expected_outcome.setter
    def expected_outcome(self, value: Optional[str]) -> None: ...
    @property
    def assertion_tasks(self) -> List[AssertionTask]:
        """All ``AssertionTask`` instances attached to this scenario."""

    @property
    def llm_judge_tasks(self) -> List[LLMJudgeTask]:
        """All ``LLMJudgeTask`` instances attached to this scenario."""

    @property
    def trace_assertion_tasks(self) -> List[TraceAssertionTask]:
        """All ``TraceAssertionTask`` instances attached to this scenario."""

    @property
    def agent_assertion_tasks(self) -> List[AgentAssertionTask]:
        """All ``AgentAssertionTask`` instances attached to this scenario."""

    @property
    def has_tasks(self) -> bool:
        """Return True when at least one task of any type is attached."""

class TasksFile:
    """Object representing a collection of evaluation tasks loaded from a file."""

    def __iter__(self) -> Iterator[AssertionTask | LLMJudgeTask | TraceAssertionTask]:
        """Iterate over all tasks in the file, yielding each task object."""

    def __next__(self) -> AssertionTask | LLMJudgeTask | TraceAssertionTask:
        """Return the next task in the file, or raise StopIteration when done."""

    @overload
    def __getitem__(self, index: int) -> AssertionTask | LLMJudgeTask | TraceAssertionTask: ...
    @overload
    def __getitem__(self, index: slice) -> List[AssertionTask | LLMJudgeTask | TraceAssertionTask]: ...
    def __getitem__(  # type: ignore[misc]
        self, index: int | slice
    ) -> AssertionTask | LLMJudgeTask | TraceAssertionTask | List[AssertionTask | LLMJudgeTask | TraceAssertionTask]:
        """Get task(s) by index or slice."""

    def __len__(self) -> int:
        """Return the total number of tasks in the file."""

    def __str__(self) -> str:
        """Return string representation of the tasks file and its contents."""

    @staticmethod
    def from_path(path: Path) -> "TasksFile":
        """Load evaluation tasks from a YAML file at the specified path.

        Args:
            path (Path):
                Path to the YAML file containing evaluation task definitions.
        """

class EvalScenarios:
    """Collection of evaluation scenarios with associated data and results.

    Holds scenario definitions, internal evaluation state, and output results
    populated by ``EvalRunner``.

    Args:
        scenarios: List of ``EvalScenario`` instances to evaluate.
    """

    scenarios: List[EvalScenario]
    metrics: Optional[EvalMetrics]

    def __init__(self, scenarios: List[EvalScenario]) -> None: ...
    def __str__(self) -> str: ...
    @property
    def dataset_results(self) -> Dict[str, "EvalResults"]:
        """Sub-agent evaluation results keyed by alias."""

    @property
    def scenario_results(self) -> List[ScenarioResult]:
        """Per-scenario evaluation results."""

    def __len__(self) -> int:
        """Return the number of scenarios."""

    def __bool__(self) -> bool:
        """Return True if there are scenarios."""

    def is_evaluated(self) -> bool:
        """Return True if evaluation has been run (metrics are populated)."""

    def model_dump_json(self) -> str:
        """Serialize to a JSON string."""

    @staticmethod
    def model_validate_json(json_string: str) -> "EvalScenarios":
        """Deserialize from a JSON string."""

    @staticmethod
    def from_path(path: Path) -> "EvalScenarios":
        """Load eval scenarios from a file.

        Supports ``.jsonl`` (one scenario per line with flat task list),
        ``.json`` (array or ``{"collection_id": "...", "scenarios": [...]}``
        wrapper), and ``.yaml``/``.yml``.

        Tasks in the file use a flat list with a ``task_type`` discriminator
        (``"Assertion"``, ``"LLMJudge"``, ``"TraceAssertion"``,
        ``"AgentAssertion"``). If no ``collection_id`` is present a new UUID7
        is generated automatically.

        Args:
            path: Path to the scenarios file.
        """

class EvalRunner:
    """Stateful evaluation engine that orchestrates scenario evaluation.

    Owns scenario definitions and profiles (as shared references).
    Provides ``collect_scenario_data()`` to populate scenario data and
    ``evaluate()`` to run multi-level evaluation, pulling spans from
    the global capture buffer automatically.

    Args:
        scenarios: List of ``EvalScenario`` instances to evaluate.
        profiles: Map of alias → ``AgentEvalProfile`` for sub-agent evaluation.
    """

    @property
    def scenarios(self) -> EvalScenarios:
        """The internal ``EvalScenarios`` container."""

    def __init__(
        self,
        scenarios: "EvalScenarios",
        profiles: Dict[str, "AgentEvalProfile"],
    ) -> None: ...
    def collect_scenario_data(
        self,
        records: Dict[str, List["EvalRecord"]],
        response: Any,
        scenario: "EvalScenario",
    ) -> None:
        """Populate scenario data for evaluation."""

    def evaluate(
        self,
        config: Optional["EvaluationConfig"] = None,
    ) -> "ScenarioEvalResults":
        """Run multi-level evaluation.

        Spans are pulled automatically from the global capture buffer.

        Args:
            config: Optional evaluation configuration.
        """

AgentFn = Callable[[str], str]

class EvalOrchestrator:
    """Manages the capture lifecycle, routes scenario types, and delegates to the Rust EvalRunner.

    Works out of the box — pass ``agent_fn`` and call ``run()``.

    Args:
        queue: ScouterQueue instance (source of profiles + capture lifecycle).
        scenarios: Scenario definitions to evaluate.
        agent_fn: Optional callable ``(query) -> response_str``.  Called once
            for ``initial_query`` and once per ``predefined_turns`` entry.
    """

    def __init__(
        self,
        queue: "ScouterQueue",
        scenarios: EvalScenarios,
        agent_fn: Optional[AgentFn] = None,
    ) -> None: ...
    def execute_agent(
        self,
        scenario: EvalScenario,
    ) -> str:
        """Execute the agent for a scenario.

        Default calls ``agent_fn(initial_query)`` then each
        ``predefined_turns`` entry.  Override to customize.

        Args:
            scenario: The scenario to execute.

        Returns:
            The agent's final response string.
        """

    def on_scenario_start(self, scenario: EvalScenario) -> None:
        """Hook called before a scenario is executed."""

    def on_scenario_complete(self, scenario: EvalScenario, response: str) -> None:
        """Hook called after a scenario is executed."""

    def on_evaluation_complete(self, results: ScenarioEvalResults) -> ScenarioEvalResults:
        """Hook called after evaluation completes. Override to post-process results."""

    def run(self, config: Optional[EvaluationConfig] = None) -> ScenarioEvalResults:
        """Execute all scenarios and return evaluation results.

        Args:
            config: Optional evaluation configuration.

        Returns:
            ScenarioEvalResults with metrics across all scenarios.
        """

__all__ = [
    "EvalOrchestrator",
    "EvaluationTaskType",
    "ComparisonOperator",
    "AssertionTask",
    "LLMJudgeTask",
    "AssertionResult",
    "AssertionResults",
    "SpanStatus",
    "AggregationType",
    "SpanFilter",
    "TraceAssertion",
    "TraceAssertionTask",
    "AgentAssertion",
    "AgentAssertionTask",
    "execute_agent_assertion_tasks",
    "TasksFile",
    "EvalScenario",
    "EvalScenarios",
    "EvalRunner",
    "EvalMetrics",
    "ScenarioResult",
    "ScenarioDelta",
    "ScenarioComparisonResults",
    "ScenarioEvalResults",
    "TaskSummary",
]
