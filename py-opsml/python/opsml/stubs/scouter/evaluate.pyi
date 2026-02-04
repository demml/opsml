#### begin imports ####

from typing import Any, Dict, List, Optional, Sequence

from ..header import SerializedType
from ..genai.potato import Prompt
from .tracing import TraceSpan

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
        - Top-level context values when field_path is None
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
        ...     field_path="response.user.age",
        ...     operator=ComparisonOperator.GreaterThan,
        ...     expected_value=18,
        ...     description="Verify user is an adult"
        ... )

        Checking top-level fields:

        >>> # Context at runtime: {"user": {"age": 25}}
        >>> task = AssertionTask(
        ...     id="check_age",
        ...     field_path="user.age",
        ...     operator=ComparisonOperator.GreaterThanOrEqual,
        ...     expected_value=21,
        ...     description="Check minimum age requirement"
        ... )

        Operating on entire context (no nested path):

        >>> # Context at runtime: 25
        >>> task = AssertionTask(
        ...     id="age_threshold",
        ...     field_path=None,
        ...     operator=ComparisonOperator.GreaterThan,
        ...     expected_value=18,
        ...     description="Validate age value"
        ... )

        String validation:

        >>> # Context: {"response": {"status": "completed"}}
        >>> task = AssertionTask(
        ...     id="status_check",
        ...     field_path="response.status",
        ...     operator=ComparisonOperator.Equals,
        ...     expected_value="completed",
        ...     description="Verify completion status"
        ... )

        Collection membership:

        >>> # Context: {"response": {"tags": ["valid", "processed"]}}
        >>> task = AssertionTask(
        ...     id="tag_validation",
        ...     field_path="response.tags",
        ...     operator=ComparisonOperator.Contains,
        ...     expected_value="valid",
        ...     description="Check for required tag"
        ... )

        With dependencies:

        >>> task = AssertionTask(
        ...     id="confidence_check",
        ...     field_path="response.confidence",
        ...     operator=ComparisonOperator.GreaterThan,
        ...     expected_value=0.9,
        ...     description="High confidence validation",
        ...     depends_on=["status_check"]
        ... )

    Note:
        - Field paths use dot-notation for nested access
        - Field paths are case-sensitive
        - When field_path is None, the entire context is used as the value
        - Type mismatches between actual and expected values will fail the assertion
        - Dependencies are executed before this task
    """

    def __init__(
        self,
        id: str,
        expected_value: Any,
        operator: ComparisonOperator,
        field_path: Optional[str] = None,
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
            field_path:
                Optional dot-notation path to extract value from context
                (e.g., "response.user.age"). If None, the entire context
                is used as the comparison value.
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
    def field_path(self) -> Optional[str]:
        """Dot-notation path to field in context, or None for entire context."""

    @field_path.setter
    def field_path(self, field_path: Optional[str]) -> None:
        """Set field path for value extraction."""

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
        ...     field_path="score",
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
        ...     field_path="response",
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
        ...     field_path=None,
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
        prompt: Prompt,
        expected_value: Any,
        field_path: Optional[str],
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
            field_path (Optional[str]):
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
    def field_path(self) -> Optional[str]:
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

    class ByName:
        """Filter spans by exact name match."""

        name: str
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class ByNamePattern:
        """Filter spans by regex name pattern."""

        pattern: str
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class WithAttribute:
        """Filter spans with specific attribute key."""

        key: str
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class WithAttributeValue:
        """Filter spans with specific attribute key-value pair."""

        key: str
        value: object  # PyValueWrapper is internal, expose as object
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class WithStatus:
        """Filter spans by status code."""

        status: SpanStatus
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class WithDuration:
        """Filter spans with duration constraints."""

        min_ms: Optional[float]
        max_ms: Optional[float]
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class Sequence:
        """Match a sequence of span names in order."""

        names: List[str]
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class And:
        """Combine multiple filters with AND logic."""

        filters: List[SpanFilter]
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    class Or:
        """Combine multiple filters with OR logic."""

        filters: List[SpanFilter]
        def and_(self, other: SpanFilter) -> SpanFilter: ...
        def or_(self, other: SpanFilter) -> SpanFilter: ...

    @staticmethod
    def by_name(name: str) -> "SpanFilter":
        """Filter spans by exact name match.

        Args:
            name (str):
                Exact span name to match (case-sensitive).

        Returns:
            SpanFilter that matches spans with the specified name.
        """

    @staticmethod
    def by_name_pattern(pattern: str) -> "SpanFilter":
        """Filter spans by regex name pattern.

        Args:
            pattern (str):
                Regular expression pattern to match span names.

        Returns:
            SpanFilter that matches spans whose names match the pattern.
        """

    @staticmethod
    def with_attribute(key: str) -> "SpanFilter":
        """Filter spans that have a specific attribute key.

        Args:
            key (str):
                Attribute key to check for existence.

        Returns:
            SpanFilter that matches spans with the specified attribute.
        """

    @staticmethod
    def with_attribute_value(key: str, value: "SerializedType") -> "SpanFilter":
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
    def with_status(status: SpanStatus) -> "SpanFilter":
        """Filter spans by execution status.

        Args:
            status (SpanStatus):
                SpanStatus to match (Ok, Error, or Unset).

        Returns:
            SpanFilter that matches spans with the specified status.
        """

    @staticmethod
    def with_duration(min_ms: Optional[float] = None, max_ms: Optional[float] = None) -> "SpanFilter":
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
    def sequence(names: List[str]) -> "SpanFilter":
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

    class SpanSequence:
        """Extracts a sequence of span names in order."""

        span_names: List[str]

    class SpanSet:
        """Checks for existence of all specified span names."""

        span_names: List[str]

    class SpanCount:
        """Counts spans matching a filter."""

        filter: SpanFilter

    class SpanExists:
        """Checks if any span matches a filter."""

        filter: SpanFilter

    class SpanAttribute:
        """Extracts attribute value from span matching filter."""

        filter: SpanFilter
        attribute_key: str

    class SpanDuration:
        """Extracts duration of span matching filter."""

        filter: SpanFilter

    class SpanAggregation:
        """Aggregates numeric attribute across filtered spans."""

        filter: SpanFilter
        attribute_key: str
        aggregation: AggregationType

    class TraceAttribute:
        """Extracts trace-level attribute value."""

        attribute_key: str

    @staticmethod
    def span_sequence(span_names: List[str]) -> "TraceAssertion":
        """Assert spans appear in specific order.

        Args:
            span_names (List[str]):
                List of span names that must appear sequentially.

        Returns:
            TraceAssertion that extracts the span sequence.
            Use with SequenceMatches operator.
        """

    @staticmethod
    def span_set(span_names: List[str]) -> "TraceAssertion":
        """Assert all specified spans exist (order independent).

        Args:
            span_names (List[str]):
                List of span names that must all be present.

        Returns:
            TraceAssertion that checks for span set membership.
            Use with ContainsAll operator.
        """

    @staticmethod
    def span_count(filter: SpanFilter) -> "TraceAssertion":
        """Count spans matching the filter.

        Args:
            filter (SpanFilter):
                SpanFilter defining which spans to count.

        Returns:
            TraceAssertion that extracts the span count.
            Use with numeric comparison operators.
        """

    @staticmethod
    def span_exists(filter: SpanFilter) -> "TraceAssertion":
        """Check if any span matches the filter.

        Args:
            filter (SpanFilter):
                SpanFilter defining which span to look for.

        Returns:
            TraceAssertion that extracts boolean existence.
            Use with Equals(True/False).
        """

    @staticmethod
    def span_attribute(filter: SpanFilter, attribute_key: str) -> "TraceAssertion":
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
    def span_duration(filter: SpanFilter) -> "TraceAssertion":
        """Get duration of span matching filter.

        Args:
            filter (SpanFilter):
                SpanFilter to identify the span.

        Returns:
            TraceAssertion that extracts span duration in milliseconds.
            Use with numeric comparison operators.
        """

    @staticmethod
    def span_aggregation(filter: SpanFilter, attribute_key: str, aggregation: AggregationType) -> "TraceAssertion":
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
    def trace_duration() -> "TraceAssertion":
        """Get total duration of the entire trace.

        Returns:
            TraceAssertion that extracts trace duration in milliseconds.
            Use with numeric comparison operators for SLA validation.
        """

    @staticmethod
    def trace_span_count() -> "TraceAssertion":
        """Count total spans in the trace.

        Returns:
            TraceAssertion that extracts total span count.
            Use with numeric operators to validate trace complexity.
        """

    @staticmethod
    def trace_error_count() -> "TraceAssertion":
        """Count spans with error status in the trace.

        Returns:
            TraceAssertion that counts error spans.
            Use with Equals(0) to ensure no errors occurred.
        """

    @staticmethod
    def trace_service_count() -> "TraceAssertion":
        """Count unique services involved in the trace.

        Returns:
            TraceAssertion that counts distinct services.
            Use to validate service boundaries or detect sprawl.
        """

    @staticmethod
    def trace_max_depth() -> "TraceAssertion":
        """Get maximum nesting depth of span tree.

        Returns:
            TraceAssertion that extracts max span depth.
            Use to detect deep recursion or validate call hierarchy.
        """

    @staticmethod
    def trace_attribute(attribute_key: str) -> "TraceAssertion":
        """Get trace-level attribute value.

        Args:
            attribute_key (str):
                Attribute key from trace context.

        Returns:
            TraceAssertion that extracts the trace attribute.
            Use with appropriate operators for the value type.
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

    def __str__(self) -> str:
        """Return string representation of the trace assertion task."""

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

__all__ = [
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
]
