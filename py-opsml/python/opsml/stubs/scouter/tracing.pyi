#### begin imports ####
import datetime
from types import TracebackType
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

from ..header import SerializedType
from .scouter import (
    CompressionType,
    Features,
    GenAIEvalRecord,
    GrpcConfig,
    HttpConfig,
    KafkaConfig,
    Metrics,
    RabbitMQConfig,
    RedisConfig,
    ScouterQueue,
)

#### end of imports ####

class TagRecord:
    """Represents a single tag record associated with an entity."""

    entity_type: str
    entity_id: str
    key: str
    value: str

class Attribute:
    """Represents a key-value attribute associated with a span."""

    key: str
    value: Any

class SpanEvent:
    """Represents an event within a span."""

    timestamp: datetime.datetime
    name: str
    attributes: List[Attribute]
    dropped_attributes_count: int

class SpanLink:
    """Represents a link to another span."""

    trace_id: str
    span_id: str
    trace_state: str
    attributes: List[Attribute]
    dropped_attributes_count: int

class TraceBaggageRecord:
    """Represents a single baggage record associated with a trace."""

    created_at: datetime.datetime
    trace_id: str
    scope: str
    key: str
    value: str

class TraceFilters:
    """A struct for filtering traces, generated from Rust pyclass."""

    service_name: Optional[str]
    has_errors: Optional[bool]
    status_code: Optional[int]
    start_time: Optional[datetime.datetime]
    end_time: Optional[datetime.datetime]
    limit: Optional[int]
    cursor_created_at: Optional[datetime.datetime]
    cursor_trace_id: Optional[str]

    def __init__(
        self,
        service_name: Optional[str] = None,
        has_errors: Optional[bool] = None,
        status_code: Optional[int] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        limit: Optional[int] = None,
        cursor_created_at: Optional[datetime.datetime] = None,
        cursor_trace_id: Optional[str] = None,
    ) -> None:
        """Initialize trace filters.

        Args:
            service_name:
                Service name filter
            has_errors:
                Filter by presence of errors
            status_code:
                Filter by root span status code
            start_time:
                Start time boundary (UTC)
            end_time:
                End time boundary (UTC)
            limit:
                Maximum number of results to return
            cursor_created_at:
                Pagination cursor: created at timestamp
            cursor_trace_id:
                Pagination cursor: trace ID
        """

class TraceMetricBucket:
    """Represents aggregated trace metrics for a specific time bucket."""

    bucket_start: datetime.datetime
    trace_count: int
    avg_duration_ms: float
    p50_duration_ms: Optional[float]
    p95_duration_ms: Optional[float]
    p99_duration_ms: Optional[float]
    error_rate: float

class TraceListItem:
    """Represents a summary item for a trace in a list view."""

    trace_id: str
    service_name: str
    scope: str
    root_operation: Optional[str]
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime]
    duration_ms: Optional[int]
    status_code: int
    status_message: Optional[str]
    span_count: Optional[int]
    has_errors: bool
    error_count: int
    created_at: datetime.datetime

class TraceSpan:
    """Detailed information for a single span within a trace."""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    span_name: str
    span_kind: Optional[str]
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime]
    duration_ms: Optional[int]
    status_code: int
    status_message: Optional[str]
    attributes: List[Attribute]
    events: List[SpanEvent]
    links: List[SpanLink]
    depth: int
    path: List[str]
    root_span_id: str
    span_order: int
    input: Any
    output: Any

def get_function_type(func: Callable[..., Any]) -> "FunctionType":
    """Determine the function type (sync, async, generator, async generator).

    Args:
        func (Callable[..., Any]):
            The function to analyze.
    """

def get_tracing_headers_from_current_span() -> Dict[str, str]:
    """Get tracing headers from the current active span and global propagator.

    Returns:
        Dict[str, str]:
            A dictionary of tracing headers.
    """

class OtelProtocol:
    """Enumeration of protocols for HTTP exporting."""

    HttpBinary: "OtelProtocol"
    HttpJson: "OtelProtocol"

class SpanKind:
    """Enumeration of span kinds."""

    Internal: "SpanKind"
    Server: "SpanKind"
    Client: "SpanKind"
    Producer: "SpanKind"
    Consumer: "SpanKind"

class FunctionType:
    """Enumeration of function types."""

    Sync: "FunctionType"
    Async: "FunctionType"
    SyncGenerator: "FunctionType"
    AsyncGenerator: "FunctionType"

class BatchConfig:
    """Configuration for batch exporting of spans."""

    def __init__(
        self,
        max_queue_size: int = 2048,
        scheduled_delay_ms: int = 5000,
        max_export_batch_size: int = 512,
    ) -> None:
        """Initialize the BatchConfig.

        Args:
            max_queue_size (int):
                The maximum queue size for spans. Defaults to 2048.
            scheduled_delay_ms (int):
                The delay in milliseconds between export attempts. Defaults to 5000.
            max_export_batch_size (int):
                The maximum batch size for exporting spans. Defaults to 512.
        """

def init_tracer(
    service_name: str = "scouter_service",
    scope: str = "scouter.tracer.{version}",
    transport_config: Optional[HttpConfig | KafkaConfig | RabbitMQConfig | RedisConfig | GrpcConfig] = None,
    exporter: Optional[HttpSpanExporter | GrpcSpanExporter | StdoutSpanExporter | TestSpanExporter] = None,
    batch_config: Optional[BatchConfig] = None,
    sample_ratio: Optional[float] = None,
    scouter_queue: Optional[ScouterQueue] = None,
    schema_url: Optional[str] = None,
    attributes: Optional[Dict[str, SerializedType]] = None,
) -> "BaseTracer":
    """
    Initialize the tracer for a service with dual export capability.
    ```
    ╔════════════════════════════════════════════╗
    ║          DUAL EXPORT ARCHITECTURE          ║
    ╠════════════════════════════════════════════╣
    ║                                            ║
    ║  Your Application                          ║
    ║       │                                    ║
    ║       │  init_tracer()                     ║
    ║       │                                    ║
    ║       ├──────────────────┬                 ║
    ║       │                  │                 ║
    ║       ▼                  ▼                 ║
    ║  ┌─────────────┐   ┌──────────────┐        ║
    ║  │  Transport  │   │   Optional   │        ║
    ║  │   to        │   │     OTEL     │        ║
    ║  │  Scouter    │   │  Exporter    │        ║
    ║  │  (Required) │   │              │        ║
    ║  └──────┬──────┘   └──────┬───────┘        ║
    ║         │                 │                ║
    ║         │                 │                ║
    ║    ┌────▼────┐       ┌────▼────┐           ║
    ║    │ Scouter │       │  OTEL   │           ║
    ║    │ Server  │       │Collector│           ║
    ║    └─────────┘       └─────────┘           ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    ```
    Configuration Overview:
        This function sets up a service tracer with **mandatory** export to Scouter
        and **optional** export to OpenTelemetry-compatible backends.

    ```
    ┌─ REQUIRED: Scouter Export ────────────────────────────────────────────────┐
    │                                                                           │
    │  All spans are ALWAYS exported to Scouter via transport_config:           │
    │    • HttpConfig    → HTTP endpoint (default)                              │
    │    • GrpcConfig    → gRPC endpoint                                        │
    │    • KafkaConfig   → Kafka topic                                          │
    │    • RabbitMQConfig→ RabbitMQ queue                                       │
    │    • RedisConfig   → Redis stream/channel                                 │
    │                                                                           │
    └───────────────────────────────────────────────────────────────────────────┘

    ┌─ OPTIONAL: OTEL Export ───────────────────────────────────────────────────┐
    │                                                                           │
    │  Optionally export spans to external OTEL-compatible systems:             │
    │    • HttpSpanExporter   → OTEL Collector (HTTP)                           │
    │    • GrpcSpanExporter   → OTEL Collector (gRPC)                           │
    │    • StdoutSpanExporter → Console output (debugging)                      │
    │    • TestSpanExporter   → In-memory (testing)                             │
    │                                                                           │
    │  If None: Only Scouter export is active (NoOpExporter)                    │
    │                                                                           │
    └───────────────────────────────────────────────────────────────────────────┘
    ```

    Args:
        service_name (str):
            The **required** name of the service this tracer is associated with.
            This is typically a logical identifier for the application or component.
            Default: "scouter_service"

        scope (str):
            The scope for the tracer. Used to differentiate tracers by version
            or environment.
            Default: "scouter.tracer.{version}"

        transport_config (HttpConfig | GrpcConfig | KafkaConfig | RabbitMQConfig | RedisConfig | None):

            Configuration for sending spans to Scouter. If None, defaults to HttpConfig.

            Supported transports:
                • HttpConfig     : Export to Scouter via HTTP
                • GrpcConfig     : Export to Scouter via gRPC
                • KafkaConfig    : Export to Scouter via Kafka
                • RabbitMQConfig : Export to Scouter via RabbitMQ
                • RedisConfig    : Export to Scouter via Redis

        exporter (HttpSpanExporter | GrpcSpanExporter | StdoutSpanExporter | TestSpanExporter | None):

            Optional secondary exporter for OpenTelemetry-compatible backends.
            If None, spans are ONLY sent to Scouter (NoOpExporter used internally).

            Available exporters:
                • HttpSpanExporter   : Send to OTEL Collector via HTTP
                • GrpcSpanExporter   : Send to OTEL Collector via gRPC
                • StdoutSpanExporter : Write to stdout (debugging)
                • TestSpanExporter   : Collect in-memory (testing)

        batch_config (BatchConfig | None):
            Configuration for batch span export. If provided, spans are queued
            and exported in batches. If None and the exporter supports batching,
            default batch settings apply.

            Batching improves performance for high-throughput applications.

        sample_ratio (float | None):
            Sampling ratio for tracing. A value between 0.0 and 1.0.
            All provided values are clamped between 0.0 and 1.0.
            If None, all spans are sampled (no sampling).

        scouter_queue (ScouterQueue | None):
            Optional ScouterQueue to associate with the tracer for correlated
            queue entity export alongside span data.

            This allows queue records (e.g., Features, Metrics, GenAIEvalRecord)
            to be ingested in conjunction with tracing data for enhanced
            observability.

            If None, no queue is associated with the tracer.

        schema_url (str | None):
            Optional URL pointing to the schema that describes the structure of the spans.
            This can be used by backends to validate and process spans according to a defined schema.
            This will be included with instrumentation scope.

        attributes (Dict[str, SerializedType] | None):
            Optional dictionary of attributes to set on the tracer.
            This will be included with instrumentation scope.

    Examples:
        Basic setup (Scouter only via HTTP):
            >>> init_tracer(service_name="my-service")

        Scouter via Kafka + OTEL Collector:
            >>> init_tracer(
            ...     service_name="my-service",
            ...     transport_config=KafkaConfig(brokers="kafka:9092"),
            ...     exporter=HttpSpanExporter(
            ...         export_config=OtelExportConfig(
            ...             endpoint="http://otel-collector:4318"
            ...         )
            ...     )
            ... )

        Scouter via gRPC + stdout debugging:
            >>> init_tracer(
            ...     service_name="my-service",
            ...     transport_config=GrpcConfig(server_uri="grpc://scouter:50051"),
            ...     exporter=StdoutSpanExporter()
            ... )

    Notes:
        • Spans are ALWAYS exported to Scouter via transport_config
        • OTEL export via exporter is completely optional
        • Both exports happen in parallel without blocking each other
        • Use batch_config to optimize performance for high-volume tracing

    See Also:
        - HttpConfig, GrpcConfig, KafkaConfig, RabbitMQConfig, RedisConfig
        - HttpSpanExporter, GrpcSpanExporter, StdoutSpanExporter, TestSpanExporter
        - BatchConfig
    """

class ActiveSpan:
    """Represents an active tracing span."""

    @property
    def trace_id(self) -> str:
        """Get the trace ID of the current active span.

        Returns:
            str:
                The trace ID.
        """

    @property
    def span_id(self) -> str:
        """Get the span ID of the current active span.

        Returns:
            str:
                The span ID.
        """

    @property
    def context_id(self) -> str:
        """Get the context ID of the active span."""

    def set_attribute(self, key: str, value: SerializedType) -> None:
        """Set an attribute on the active span.

        Args:
            key (str):
                The attribute key.
            value (SerializedType):
                The attribute value.
        """

    def set_tag(self, key: str, value: str) -> None:
        """Set a tag on the active span. Tags are similar to attributes
        except they are often used for indexing and searching spans/traces.
        All tags are also set as attributes on the span. Before export, tags are
        extracted and stored in a separate backend table for efficient querying.

        Args:
            key (str):
                The tag key.
            value (str):
                The tag value.
        """

    def add_event(self, name: str, attributes: Any) -> None:
        """Add an event to the active span.

        Args:
            name (str):
                The name of the event.
            attributes (Any):
                Optional attributes for the event.
                Can be any serializable type or pydantic `BaseModel`.
        """

    def add_queue_item(
        self,
        alias: str,
        item: Union[Features, Metrics, GenAIEvalRecord],
    ) -> None:
        """Helpers to add queue entities into a specified queue associated with the active span.
        This is an convenience method that abstracts away the details of queue management and
        leverages tracing's sampling capabilities to control data ingestion. Thus, correlated queue
        records and spans/traces can be sampled together based on the same sampling decision.

        Args:
            alias (str):
                Alias of the queue to add the item into.
            item (Union[Features, Metrics, GenAIEvalRecord]):
                Item to add into the queue.
                Can be an instance for Features, Metrics, or GenAIEvalRecord.

        Example:
            ```python
            features = Features(
                features=[
                    Feature("feature_1", 1),
                    Feature("feature_2", 2.0),
                    Feature("feature_3", "value"),
                ]
            )
            span.add_queue_item(alias, features)
            ```
        """

    def set_status(self, status: str, description: Optional[str] = None) -> None:
        """Set the status of the active span.

        Args:
            status (str):
                The status code (e.g., "OK", "ERROR").
            description (Optional[str]):
                Optional description for the status.
        """

    def set_input(self, input: Any, max_length: int = 1000) -> None:
        """Set the input for the active span.

        Args:
            input (Any):
                The input to set. Can be any serializable primitive type (str, int, float, bool, list, dict),
                or a pydantic `BaseModel`.
            max_length (int):
                The maximum length for a given string input. Defaults to 1000.
        """

    def set_output(self, output: Any, max_length: int = 1000) -> None:
        """Set the output for the active span.

        Args:
            output (Any):
                The output to set. Can be any serializable primitive type (str, int, float, bool, list, dict),
                or a pydantic `BaseModel`.
            max_length (int):
                The maximum length for a given string output. Defaults to 1000.

        """

    def __enter__(self) -> "ActiveSpan":
        """Enter the span context."""

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit the span context."""

    async def __aenter__(self) -> "ActiveSpan":
        """Enter the async span context."""

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit the async span context."""

class BaseTracer:
    def __init__(
        self,
        instrumenting_module_name: str = "scouter_tracer",
        instrumenting_library_version: str = "{version}",
        schema_url: Optional[str] = None,
        attributes: Optional[Dict[str, SerializedType]] = None,
        scouter_queue: Optional[ScouterQueue] = None,
    ) -> None:
        """Initialize the BaseTracer with a service name.

        Args:
            instrumenting_module_name (str):
                The name of the instrumenting module.
            instrumenting_library_version (str):
                The version of the instrumenting library.
            schema_url (Optional[str]):
                Optional URL pointing to the schema that describes the structure of the spans.
            attributes (Optional[Dict[str, SerializedType]]):
                Optional dictionary of attributes to set on the tracer.
            scouter_queue (Optional[ScouterQueue]):
                Optional ScouterQueue to associate with the tracer.
        """

    def set_scouter_queue(self, queue: "ScouterQueue") -> None:
        """Add a ScouterQueue to the tracer. This allows the tracer to manage
        and export queue entities in conjunction with span data for correlated
        monitoring and observability.

        Args:
            queue (ScouterQueue):
                The ScouterQueue instance to add.
        """

    def start_as_current_span(
        self,
        name: str,
        kind: Optional[SpanKind] = SpanKind.Internal,
        label: Optional[str] = None,
        attributes: Optional[dict[str, str]] = None,
        baggage: Optional[dict[str, str]] = None,
        tags: Optional[dict[str, str]] = None,
        parent_context_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        remote_sampled: Optional[bool] = None,
    ) -> ActiveSpan:
        """Context manager to start a new span as the current span.

        Args:
            name (str):
                The name of the span.
            kind (Optional[SpanKind]):
                The kind of span (e.g., "SERVER", "CLIENT").
            label (Optional[str]):
                An optional label for the span.
            attributes (Optional[dict[str, str]]):
                Optional attributes to set on the span.
            baggage (Optional[dict[str, str]]):
                Optional baggage items to attach to the span.
            tags (Optional[dict[str, str]]):
                Optional tags to set on the span and trace.
            parent_context_id (Optional[str]):
                Optional parent span context ID.
            trace_id (Optional[str]):
                Optional trace ID to associate with the span. This is useful for
                when linking spans across different services or systems.
            span_id (Optional[str]):
                Optional span ID to associate with the span. This will be the parent span ID.
            remote_sampled (Optional[bool]):
                Optional flag indicating if the span was sampled remotely.
        Returns:
            ActiveSpan:
        """

    def _start_decorated_as_current_span(
        self,
        name: Optional[str],
        func: Callable[..., Any],
        func_args: tuple[Any, ...],
        kind: SpanKind = SpanKind.Internal,
        label: Optional[str] = None,
        attributes: List[dict[str, str]] = [],
        baggage: List[dict[str, str]] = [],
        tags: List[dict[str, str]] = [],
        parent_context_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        max_length: int = 1000,
        func_type: FunctionType = FunctionType.Sync,
        func_kwargs: Optional[dict[str, Any]] = None,
    ) -> ActiveSpan:
        """Context manager to start a new span as the current span for decorated functions.

        Args:
            name (Optional[str]):
                The name of the span. If None, defaults to the function name.
            func (Callable[..., Any]):
                The function being decorated.
            func_args (tuple[Any, ...]):
                The positional arguments passed to the function.
            kind (SpanKind):
                The kind of span (e.g., Internal, Server, Client).
            label (Optional[str]):
                An optional label for the span.
            attributes (Optional[dict[str, str]]):
                Optional attributes to set on the span.
            baggage (Optional[dict[str, str]]):
                Optional baggage items to attach to the span.
            tags (Optional[dict[str, str]]):
                Optional tags to set on the span.
            parent_context_id (Optional[str]):
                Optional parent span context ID.
            trace_id (Optional[str]):
                Optional trace ID to associate with the span. This is useful for
                when linking spans across different services or systems.
            max_length (int):
                The maximum length for string inputs/outputs. Defaults to 1000.
            func_type (FunctionType):
                The type of function being decorated (Sync, Async, Generator, AsyncGenerator).
            func_kwargs (Optional[dict[str, Any]]):
                The keyword arguments passed to the function.
        Returns:
            ActiveSpan:
                The active span context manager.
        """

    def current_span(self) -> ActiveSpan:
        """Get the current active span.

        Returns:
            ActiveSpan:
                The current active span.
                Raises an error if no active span exists.
        """

    def shutdown(self) -> None:
        """Shutdown the tracer and flush any remaining spans."""

def get_current_active_span(self) -> ActiveSpan:
    """Get the current active span.

    Returns:
        ActiveSpan:
            The current active span.
            Raises an error if no active span exists.
    """

class StdoutSpanExporter:
    """Exporter that outputs spans to standard output (stdout)."""

    def __init__(
        self,
        batch_export: bool = False,
        sample_ratio: Optional[float] = None,
    ) -> None:
        """Initialize the StdoutSpanExporter.

        Args:
            batch_export (bool):
                Whether to use batch exporting. Defaults to False.
            sample_ratio (Optional[float]):
                The sampling ratio for traces. If None, defaults to always sample.
        """

    @property
    def batch_export(self) -> bool:
        """Get whether batch exporting is enabled."""

    @property
    def sample_ratio(self) -> Optional[float]:
        """Get the sampling ratio."""

def flush_tracer() -> None:
    """Force flush the tracer's exporter."""

class OtelExportConfig:
    """Configuration for exporting spans."""

    def __init__(
        self,
        endpoint: Optional[str],
        protocol: OtelProtocol = OtelProtocol.HttpBinary,
        timeout: Optional[int] = None,
        compression: Optional[CompressionType] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        """Initialize the ExportConfig.

        Args:
            endpoint (Optional[str]):
                The endpoint for exporting spans. Can be either an HTTP or gRPC endpoint.
            protocol (Protocol):
                The protocol to use for exporting spans. Defaults to HttpBinary.
            timeout (Optional[int]):
                The timeout for requests in seconds.
            compression (Optional[CompressionType]):
                The compression type for requests.
            headers (Optional[dict[str, str]]):
                Optional HTTP headers to include in requests.
        """

    @property
    def endpoint(self) -> Optional[str]:
        """Get the HTTP endpoint for exporting spans."""

    @property
    def protocol(self) -> OtelProtocol:
        """Get the protocol used for exporting spans."""

    @property
    def timeout(self) -> Optional[int]:
        """Get the timeout for requests in seconds."""

    @property
    def compression(self) -> Optional[CompressionType]:
        """Get the compression type used for exporting spans."""

    @property
    def headers(self) -> Optional[dict[str, str]]:
        """Get the HTTP headers used for exporting spans."""

class HttpSpanExporter:
    """Exporter that sends spans to an HTTP endpoint."""

    def __init__(
        self,
        batch_export: bool = True,
        export_config: Optional[OtelExportConfig] = None,
        sample_ratio: Optional[float] = None,
    ) -> None:
        """Initialize the HttpSpanExporter.

        Args:
            batch_export (bool):
                Whether to use batch exporting. Defaults to True.
            export_config (Optional[OtelExportConfig]):
                Configuration for exporting spans.
            sample_ratio (Optional[float]):
                The sampling ratio for traces. If None, defaults to always sample.
        """

    @property
    def sample_ratio(self) -> Optional[float]:
        """Get the sampling ratio."""

    @property
    def batch_export(self) -> bool:
        """Get whether batch exporting is enabled."""

    @property
    def endpoint(self) -> Optional[str]:
        """Get the HTTP endpoint for exporting spans."""

    @property
    def protocol(self) -> OtelProtocol:
        """Get the protocol used for exporting spans."""

    @property
    def timeout(self) -> Optional[int]:
        """Get the timeout for HTTP requests in seconds."""

    @property
    def headers(self) -> Optional[dict[str, str]]:
        """Get the HTTP headers used for exporting spans."""

    @property
    def compression(self) -> Optional[CompressionType]:
        """Get the compression type used for exporting spans."""

class GrpcSpanExporter:
    """Exporter that sends spans to a gRPC endpoint."""

    def __init__(
        self,
        batch_export: bool = True,
        export_config: Optional[OtelExportConfig] = None,
        sample_ratio: Optional[float] = None,
    ) -> None:
        """Initialize the GrpcSpanExporter.

        Args:
            batch_export (bool):
                Whether to use batch exporting. Defaults to True.
            export_config (Optional[OtelExportConfig]):
                Configuration for exporting spans.
            sample_ratio (Optional[float]):
                The sampling ratio for traces. If None, defaults to always sample.
        """

    @property
    def sample_ratio(self) -> Optional[float]:
        """Get the sampling ratio."""

    @property
    def batch_export(self) -> bool:
        """Get whether batch exporting is enabled."""

    @property
    def endpoint(self) -> Optional[str]:
        """Get the gRPC endpoint for exporting spans."""

    @property
    def protocol(self) -> OtelProtocol:
        """Get the protocol used for exporting spans."""

    @property
    def timeout(self) -> Optional[int]:
        """Get the timeout for gRPC requests in seconds."""

    @property
    def compression(self) -> Optional[CompressionType]:
        """Get the compression type used for exporting spans."""

class TraceRecord:
    created_at: datetime.datetime
    trace_id: str
    space: str
    name: str
    version: str
    scope: str
    trace_state: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    duration_ms: int
    status: str
    root_span_id: str
    attributes: Optional[dict]

    def get_attributes(self) -> Dict[str, Any]: ...

class TraceSpanRecord:
    created_at: datetime.datetime
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    space: str
    name: str
    version: str
    scope: str
    span_name: str
    span_kind: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    duration_ms: int
    status_code: str
    status_message: str
    attributes: dict
    events: dict
    links: dict

    def get_attributes(self) -> Dict[str, Any]: ...
    def get_events(self) -> Dict[str, Any]: ...
    def get_links(self) -> Dict[str, Any]: ...
    def __str__(self) -> str: ...

class TestSpanExporter:
    """Exporter for testing that collects spans in memory."""

    def __init__(self, batch_export: bool = True) -> None:
        """Initialize the TestSpanExporter.

        Args:
            batch_export (bool):
                Whether to use batch exporting. Defaults to True.
        """

    @property
    def traces(self) -> list[TraceRecord]:
        """Get the collected trace records."""

    @property
    def spans(self) -> list[TraceSpanRecord]:
        """Get the collected trace span records."""

    @property
    def baggage(self) -> list[TraceBaggageRecord]:
        """Get the collected trace baggage records."""

    def clear(self) -> None:
        """Clear all collected trace records."""

def shutdown_tracer() -> None:
    """Shutdown the tracer and flush any remaining spans."""

__all__ = [
    "init_tracer",
    "SpanKind",
    "FunctionType",
    "ActiveSpan",
    "OtelExportConfig",
    "GrpcConfig",
    "GrpcSpanExporter",
    "HttpSpanExporter",
    "StdoutSpanExporter",
    "OtelProtocol",
    "TraceRecord",
    "TraceSpanRecord",
    "TraceBaggageRecord",
    "TestSpanExporter",
    "flush_tracer",
    "BatchConfig",
    "shutdown_tracer",
    "TraceMetricsRequest",
]
