#### begin imports ####
# ty:ignore[unresolved-import]

import datetime
from types import TracebackType
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from ..header import SerializedType
from .mock import MockConfig
from .scouter import (
    CompressionType,
    GrpcConfig,
    HttpConfig,
    KafkaConfig,
    RabbitMQConfig,
    RedisConfig,
    ScouterQueue,
)

HAS_OPENTELEMETRY = True
if TYPE_CHECKING:
    from opentelemetry.trace import SpanContext
else:
    # Try to import OpenTelemetry, but provide fallbacks if not available
    try:
        from opentelemetry.trace import SpanContext

        HAS_OPENTELEMETRY = True
    except ImportError:
        HAS_OPENTELEMETRY = False

        class SpanContext:
            """Fallback SpanContext if OpenTelemetry is not installed."""

            pass

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

    clause: Optional[Any]
    start_time: Optional[datetime.datetime]
    end_time: Optional[datetime.datetime]
    limit: Optional[int]
    cursor_start_time: Optional[datetime.datetime]
    cursor_trace_id: Optional[str]
    direction: Optional[str]
    trace_ids: Optional[List[str]]
    entity_uid: Optional[str]

    def __init__(
        self,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        limit: Optional[int] = None,
        cursor_start_time: Optional[datetime.datetime] = None,
        cursor_trace_id: Optional[str] = None,
        direction: Optional[str] = None,
        trace_ids: Optional[List[str]] = None,
        entity_uid: Optional[str] = None,
    ) -> None:
        """Initialize trace filters.

        Args:
            start_time:
                Start time boundary (UTC)
            end_time:
                End time boundary (UTC)
            limit:
                Maximum number of results to return
            cursor_start_time:
                Pagination cursor: trace start timestamp
            cursor_trace_id:
                Pagination cursor: trace ID
            direction:
                Pagination direction
            trace_ids:
                List of trace IDs to filter by
            entity_uid:
                Filter by associated entity UID
        """

    @classmethod
    def from_query(cls, q: str) -> "TraceFilters":
        """Build TraceFilters from the trace search DSL."""

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

class ScouterResourceConfig:
    """Process-wide OpenTelemetry Resource configuration for Scouter tracing.

    Resource attributes describe the process emitting telemetry. They are
    independent from an individual tracer's instrumentation scope. Scouter
    resolves service identity using OpenTelemetry precedence:
    explicit constructor values > OTEL_SERVICE_NAME > OTEL_RESOURCE_ATTRIBUTES >
    "unknown_service".

    Attributes:
        service_name:
            Logical service name for the process, written to the OTel
            `service.name` Resource attribute.
        service_version:
            Optional version for the running service, written to
            `service.version`.
        service_namespace:
            Optional namespace for the running service, written to
            `service.namespace`.
        service_instance_id:
            Optional stable instance identifier. When unset, Scouter generates a
            UUIDv4 value for `service.instance.id`.
        extra_attributes:
            Additional Resource attributes to attach to every exported span.
            Explicit values override matching keys from OTEL_RESOURCE_ATTRIBUTES.
    """

    service_name: Optional[str]
    service_version: Optional[str]
    service_namespace: Optional[str]
    service_instance_id: Optional[str]
    extra_attributes: Dict[str, str]

    def __init__(
        self,
        service_name: Optional[str] = None,
        service_version: Optional[str] = None,
        service_namespace: Optional[str] = None,
        service_instance_id: Optional[str] = None,
        extra_attributes: Optional[Dict[str, str]] = None,
    ) -> None:
        """Create a Resource configuration.

        Args:
            service_name:
                Explicit `service.name`. If omitted, Scouter checks
                OTEL_SERVICE_NAME, then OTEL_RESOURCE_ATTRIBUTES, then defaults
                to "unknown_service".
            service_version:
                Explicit `service.version`.
            service_namespace:
                Explicit `service.namespace`.
            service_instance_id:
                Explicit `service.instance.id`. If omitted, Scouter generates a
                UUIDv4 instance ID.
            extra_attributes:
                Additional Resource attributes. These override matching
                OTEL_RESOURCE_ATTRIBUTES keys.
        """

def configure_tracing(
    resource_config: Optional[ScouterResourceConfig] = None,
    transport_config: Optional[
        HttpConfig | KafkaConfig | RabbitMQConfig | RedisConfig | GrpcConfig | MockConfig
    ] = None,
    exporter: Optional[HttpSpanExporter | GrpcSpanExporter | StdoutSpanExporter | TestSpanExporter] = None,
    batch_config: Optional[BatchConfig] = None,
    sample_ratio: Optional[float] = None,
) -> None:
    """Configure the process-wide tracer provider exactly once.

    This builds the Rust `SdkTracerProvider`, attaches the Scouter exporter,
    optionally attaches a secondary OTEL exporter, and stores the provider in a
    process-wide singleton. Subsequent calls log a warning and are no-ops,
    matching OpenTelemetry's `set_tracer_provider` behavior.

    Resource identity is resolved from `resource_config` and the OTEL
    environment variables. Instrumentation scope identity is not set here; call
    `get_tracer()` with a `scope_name` and optional `scope_version` for that.

    Args:
        resource_config:
            Optional process Resource configuration. If omitted, Scouter builds
            one from OTEL_SERVICE_NAME, OTEL_RESOURCE_ATTRIBUTES, and defaults.
        transport_config:
            Optional Scouter transport configuration. If omitted, Scouter uses
            gRPC by default, or an offline mock transport when SCOUTER_OFFLINE=1.
        exporter:
            Optional secondary OTEL exporter, such as HTTP, gRPC, stdout, or the
            in-memory test exporter. Scouter export is always configured
            separately through `transport_config`.
        batch_config:
            Optional batch span processor settings.
        sample_ratio:
            Optional trace sampling ratio. Values outside [0.0, 1.0] are
            clamped by the Rust tracer provider.
    """

def get_tracer(
    scope_name: str,
    scope_version: Optional[str] = None,
    schema_url: Optional[str] = None,
    scope_attributes: Optional[Dict[str, Any]] = None,
    default_attributes: Optional[Dict[str, Any]] = None,
    scouter_queue: Optional[Any] = None,
) -> "BaseTracer":
    """Get a tracer for an instrumenting library/module.

    `scope_name` and `scope_version` populate the OpenTelemetry
    InstrumentationScope. They are independent of the process-wide
    `service.name` Resource configured by `configure_tracing()`.

    If `configure_tracing()` has not been called, Scouter lazily configures a
    provider from environment-derived Resource defaults before returning the
    tracer.

    Args:
        scope_name:
            Name of the instrumenting library or module, for example
            "httpx", "fastapi", or "opsml.agent".
        scope_version:
            Optional version for the instrumenting library or module.
        schema_url:
            Optional OpenTelemetry schema URL associated with the scope.
        scope_attributes:
            Optional attributes attached to the InstrumentationScope.
        default_attributes:
            Optional attributes to apply to every span created by this tracer.
        scouter_queue:
            Optional queue used to correlate queue records with spans.

    Returns:
        A low-level `BaseTracer` bound to the requested instrumentation scope.
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

    @property
    def parent_context_id(self) -> Optional[str]:
        """Get the parent context ID of the active span."""

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

    def add_event(
        self,
        name: str,
        attributes: SerializedType,
        timestamp: Optional[int] = None,
    ) -> None:
        """Add an event to the active span.

        Args:
            name (str):
                The name of the event.
            attributes (SerializedType):
                Optional attributes for the event.
                Can be any serializable type or pydantic `BaseModel`.
            timestamp (Optional[int]):
                Optional timestamp for the event. Defaults to None.
        """

    def attach_eval(
        self,
        profile_uid: str,
        context: Any,
        *,
        record_id: Optional[str] = None,
        session_id: Optional[str] = None,
        media: Optional[List[Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        """Build and insert a trace-anchored EvalRecord for this span."""

    def set_status(self, status: str, description: Optional[str] = None) -> None:
        """Set the status of the active span.

        Args:
            status (str):
                The status code (e.g., "OK", "ERROR").
            description (Optional[str]):
                Optional description for the status.
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

    def end(self, end_time: Optional[int] = None) -> None:
        """End the span."""

    def _end_with_cleanup(self, end_time: Optional[int] = None) -> None:
        """End the span and run full cleanup without direct ContextVar reset."""

    def get_span_context(self) -> "SpanContext":
        """Get the span context for the active span

        Returns:
            Otel SpanContext.
        """

    def set_attributes(self, attributes: Dict[str, SerializedType]) -> None:
        """Set multiple attributes on the active span from a dictionary.

        Args:
            attributes (Dict[str, SerializedType]):
                A dictionary of attributes to set on the span. Keys are attribute names,
                and values can be any serializable type or pydantic `BaseModel`.
        """

    def update_name(self, name: str) -> None:
        """Update the name of the active span.

        Args:
            name (str):
                The new name for the span.
        """

    def is_recording(self) -> bool:
        """Check if the active span is recording.

        Returns:
            bool:
                True if the span is recording, False otherwise.
        """

    def record_exception(
        self,
        exception: Exception,
        attributes: Optional[Dict[str, SerializedType]] = None,
        timestamp: Optional[int] = None,
        escaped: bool = False,
    ) -> None:
        """Record an exception in the active span.

        Args:
            exception (Exception):
                The exception to record.
            attributes (Optional[Dict[str, SerializedType]]):
                Optional attributes to associate with the exception.
            timestamp (Optional[int]):
                Optional timestamp for the exception.
            escaped (bool):
                Whether the exception was escaped.
        """

    def add_link(
        self,
        context: "SpanContext",
        attributes: Optional[SerializedType] = None,
    ) -> None:
        """Add a link to another span.

        Args:
            context (SpanContext):
                The span context to link to.
            attributes (Optional[SerializedType]):
                Optional attributes for the link.
        """

class BaseTracer:
    def __init__(
        self,
        scope_name: str,
        scope_version: Optional[str] = None,
        schema_url: Optional[str] = None,
        scope_attributes: Optional[Dict[str, SerializedType]] = None,
        default_attributes: Optional[Dict[str, SerializedType]] = None,
        queue: Optional[ScouterQueue] = None,
    ) -> None:
        """Initialize the BaseTracer with an instrumentation scope.

        Args:
            scope_name (str):
                The name of the instrumenting module.
            scope_version (Optional[str]):
                The version of the instrumenting module.
            schema_url (Optional[str]):
                Optional URL pointing to the schema that describes the structure of the spans.
            scope_attributes (Optional[Dict[str, SerializedType]]):
                Optional dictionary of attributes to set on the instrumentation scope.
            default_attributes (Optional[Dict[str, SerializedType]]):
                Optional dictionary of attributes to set on every span.
            queue (Optional[ScouterQueue]):
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

    def start_span(
        self,
        name: str,
        context: Optional[Any] = None,
        kind: Optional[SpanKind] = SpanKind.Internal,
        attributes: Optional[Any] = None,
        baggage: Optional[List[dict[str, str]]] = None,
        tags: Optional[List[dict[str, str]]] = None,
        label: Optional[str] = None,
        parent_context_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        remote_sampled: Optional[bool] = None,
        headers: Optional[dict[str, str]] = None,
        links: Optional[Any] = None,
        start_time: Optional[int] = None,
        record_exception: Optional[bool] = None,
        set_status_on_exception: Optional[bool] = None,
    ) -> ActiveSpan:
        """Start a span without pushing it as the current active span."""

    def start_as_current_span(
        self,
        name: str,
        context: Optional[Any] = None,
        kind: Optional[SpanKind] = SpanKind.Internal,
        attributes: Optional[Any] = None,
        baggage: Optional[List[dict[str, str]]] = None,
        tags: Optional[List[dict[str, str]]] = None,
        label: Optional[str] = None,
        parent_context_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        remote_sampled: Optional[bool] = None,
        headers: Optional[dict[str, str]] = None,
        links: Optional[Any] = None,
        start_time: Optional[int] = None,
        record_exception: Optional[bool] = None,
        set_status_on_exception: Optional[bool] = None,
    ) -> ActiveSpan:
        """Context manager to start a new span as the current span.

        Args:
            name (str):
                The name of the span.
            context (Optional[Any]):
                OTel Python Context object from auto-instrumentors (StarletteInstrumentor, etc.).
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
            headers (Optional[dict[str, str]]):
                W3C traceparent/tracestate headers from an upstream service.
                Takes priority over explicit trace_id/span_id params.
            links (Optional[Any]):
                Accepted for OTel compatibility; not yet used.
            start_time (Optional[int]):
                Accepted for OTel compatibility; not yet used.
            record_exception (Optional[bool]):
                Accepted for OTel compatibility; not yet used.
            set_status_on_exception (Optional[bool]):
                Accepted for OTel compatibility; not yet used.
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

    @property
    def current_span(self) -> ActiveSpan:
        """Get the current active span.

        Returns:
            ActiveSpan:
                The current active span.
                Raises an error if no active span exists.
        """

    def shutdown(self) -> None:
        """Shutdown the tracer and flush any remaining spans."""

    def enable_local_capture(self, capture_run_id: str) -> None:
        """Enable local span capture mode for a capture run."""

    def disable_local_capture(self, capture_run_id: str) -> None:
        """Disable local span capture mode for a capture run."""

    def drain_local_spans(self, capture_run_id: str) -> List[TraceSpanRecord]:
        """Drain and return locally captured spans for a capture run."""

    def get_local_spans_by_trace_ids(self, capture_run_id: str, trace_ids: List[str]) -> List[TraceSpanRecord]:
        """Return spans matching the given trace_ids without draining the run buffer."""

def get_current_active_span() -> ActiveSpan:
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

def reset_tracer_provider() -> None:
    """Reset the process-wide Rust tracer provider."""

def enable_local_span_capture(capture_run_id: str) -> None:
    """Enable in-process span capture for a capture run."""

def disable_local_span_capture(capture_run_id: str) -> None:
    """Disable in-process span capture for a capture run."""

def drain_local_span_capture(capture_run_id: str) -> List[TraceSpanRecord]:
    """Drain and return locally captured spans for a capture run."""

def extract_span_context_from_headers(
    headers: Dict[str, str],
) -> Optional[Dict[str, str]]:
    """Extract span context from W3C traceparent headers (or legacy trace_id/span_id keys).

    Returns a dict with 'trace_id', 'span_id', 'is_sampled' keys, or None if no valid context found.
    """

__all__ = [
    "ScouterResourceConfig",
    "configure_tracing",
    "get_tracer",
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
    "reset_tracer_provider",
    "extract_span_context_from_headers",
]
