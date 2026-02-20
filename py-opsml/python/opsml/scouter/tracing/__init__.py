# pylint: disable=dangerous-default-value,implicit-str-concat
# mypy: disable-error-code="attr-defined"

import functools
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Collection,
    Generator,
    List,
    Mapping,
    Optional,
    ParamSpec,
    Sequence,
    TypeAlias,
    TypeVar,
    Union,
    cast,
)

from ..._opsml import (
    ActiveSpan,
    BaseTracer,
    BatchConfig,
    FunctionType,
    GrpcConfig,
    GrpcSpanExporter,
    HttpConfig,
    HttpSpanExporter,
    KafkaConfig,
    OtelExportConfig,
    OtelProtocol,
    RabbitMQConfig,
    RedisConfig,
    ScouterQueue,
    SpanKind,
    StdoutSpanExporter,
    TestSpanExporter,
    TraceBaggageRecord,
    TraceRecord,
    TraceSpanRecord,
    flush_tracer,
    get_current_active_span,
    get_function_type,
    get_tracing_headers_from_current_span,
    init_tracer,
    shutdown_tracer,
)

SerializedType: TypeAlias = Union[str, int, float, dict, list]
P = ParamSpec("P")
R = TypeVar("R")
HAS_OPENTELEMETRY = True
if TYPE_CHECKING:
    from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
    from opentelemetry.trace import Tracer as _OtelTracer
    from opentelemetry.trace import TracerProvider as _OtelTracerProvider
    from opentelemetry.trace import set_tracer_provider
    from opentelemetry.util.types import Attributes
else:
    # Try to import OpenTelemetry, but provide fallbacks if not available
    try:
        from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
        from opentelemetry.trace import get_tracer_provider, set_tracer_provider

        HAS_OPENTELEMETRY = True
    except ImportError:
        HAS_OPENTELEMETRY = False

        # Provide stub base class when OpenTelemetry is not installed
        class BaseInstrumentor:
            """Stub base class when OpenTelemetry is not available."""

            def instrument(self, **kwargs):
                raise ImportError(
                    "OpenTelemetry is not installed. Install with: "
                    "pip install opsml[opentelemetry]"
                )

            def uninstrument(self, **kwargs):
                raise ImportError(
                    "OpenTelemetry is not installed. Install with: "
                    "pip install opsml[opentelemetry]"
                )

        def get_tracer_provider():
            raise ImportError(
                "OpenTelemetry is not installed. Install with: "
                "pip install opsml[opentelemetry]"
            )

        def set_tracer_provider(provider):
            raise ImportError(
                "OpenTelemetry is not installed. Install with: "
                "pip install opsml[opentelemetry]"
            )

    class _OtelTracerProvider:
        pass

    class _OtelTracer:
        pass

    AttributeValue = Union[
        str,
        bool,
        int,
        float,
        Sequence[str],
        Sequence[bool],
        Sequence[int],
        Sequence[float],
    ]

    Attributes = Optional[Mapping[str, AttributeValue]]


def set_output(
    span: ActiveSpan,
    outputs: List[Any],
    max_length: int,
    capture_last_stream_item: bool = False,
    join_stream_items: bool = False,
) -> None:
    """Helper to set output attribute on span with length check."""

    if capture_last_stream_item and outputs:
        span.set_output(outputs[-1], max_length)

    elif join_stream_items:
        span.set_output("".join(outputs), max_length)

    else:
        span.set_output(outputs, max_length)


class Tracer(BaseTracer):
    """
    Extended tracer with decorator support.

    This class extends the Rust BaseTracer to provide Python-friendly
    decorator functionality for tracing spans.

    Examples:
        >>> from scouter.tracing import init_tracer, get_tracer
        >>> init_tracer(name="my-service")
        >>> tracer = get_tracer("my-service")
        >>>
        >>> @tracer.span("operation_name")
        ... def my_function():
        ...     return "result"
    """

    def span(
        self,
        name: Optional[str] = None,
        kind: SpanKind = SpanKind.Internal,
        attributes: List[dict[str, str]] = [],
        baggage: List[dict[str, str]] = [],
        tags: List[dict[str, str]] = [],
        label: Optional[str] = None,
        parent_context_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        max_length: int = 1000,
        capture_last_stream_item: bool = False,
        join_stream_items: bool = False,
        **kwargs,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Decorator to trace function execution with OpenTelemetry spans.

        Args:
            name (Optional[str]):
                The name of the span. If None, defaults to the function name.
            kind (SpanKind):
                The kind of span (default: Internal)
            attributes (List[dict[str, str]]):
                Additional attributes to set on the span
            baggage (List[dict[str, str]]):
                Additional baggage to set on the span
            tags (List[dict[str, str]]):
                Additional tags to set on the span
            label (Optional[str]):
                An optional label for the span
            parent_context_id (Optional[str]):
                Parent context ID for the span
            trace_id (Optional[str]):
                Optional trace ID to associate with the span. This is useful for
            max_length (int):
                Maximum length for input/output capture
            capture_last_stream_item (bool):
                Whether to capture only the last item from streaming functions
            join_stream_items (bool):
                Whether to join all stream items into a single string for output
            **kwargs:
                Additional keyword arguments
        Returns:
            Callable[[Callable[P, R]], Callable[P, R]]:
        """

        # I'd prefer this entire decorator to be rust, but creating this type of decorator in rust
        # is a little bit of a pain when dealing with async
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            span_name = name or f"{func.__module__}.{func.__qualname__}"
            function_type = get_function_type(func)

            if function_type == FunctionType.AsyncGenerator:

                @functools.wraps(func)
                async def async_generator_wrapper(
                    *args: P.args, **kwargs: P.kwargs
                ) -> Any:
                    async with self._start_decorated_as_current_span(
                        name=span_name,
                        func=func,
                        func_args=args,
                        kind=kind,
                        attributes=attributes,
                        baggage=baggage,
                        tags=tags,
                        label=label,
                        parent_context_id=parent_context_id,
                        trace_id=trace_id,
                        max_length=max_length,
                        func_type=function_type,
                        func_kwargs=kwargs,
                    ) as span:
                        try:
                            async_gen_func = cast(
                                Callable[P, AsyncGenerator[Any, None]], func
                            )
                            generator = async_gen_func(*args, **kwargs)

                            outputs = []
                            async for item in generator:
                                outputs.append(item)
                                yield item

                            set_output(
                                span,
                                outputs,
                                max_length,
                                capture_last_stream_item,
                                join_stream_items,
                            )

                        except Exception as e:
                            span.set_attribute("error.type", type(e).__name__)
                            raise

                return cast(Callable[P, R], async_generator_wrapper)

            if function_type == FunctionType.SyncGenerator:

                @functools.wraps(func)
                def generator_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                    with self._start_decorated_as_current_span(
                        name=span_name,
                        func=func,
                        func_args=args,
                        kind=kind,
                        attributes=attributes,
                        baggage=baggage,
                        tags=tags,
                        label=label,
                        parent_context_id=parent_context_id,
                        trace_id=trace_id,
                        max_length=max_length,
                        func_type=function_type,
                        func_kwargs=kwargs,
                    ) as span:
                        try:
                            gen_func = cast(
                                Callable[P, Generator[Any, None, None]], func
                            )
                            generator = gen_func(*args, **kwargs)
                            results = []

                            for item in generator:
                                results.append(item)
                                yield item

                            set_output(
                                span,
                                results,
                                max_length,
                                capture_last_stream_item,
                                join_stream_items,
                            )

                        except Exception as e:
                            span.set_attribute("error.type", type(e).__name__)
                            raise

                return cast(Callable[P, R], generator_wrapper)

            if function_type == FunctionType.Async:

                @functools.wraps(func)
                async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                    async with self._start_decorated_as_current_span(
                        name=span_name,
                        func=func,
                        func_args=args,
                        kind=kind,
                        attributes=attributes,
                        baggage=baggage,
                        tags=tags,
                        label=label,
                        parent_context_id=parent_context_id,
                        trace_id=trace_id,
                        max_length=max_length,
                        func_type=function_type,
                        func_kwargs=kwargs,
                    ) as span:
                        try:
                            async_func = cast(Callable[P, Awaitable[Any]], func)
                            result = await async_func(*args, **kwargs)

                            span.set_output(result, max_length)
                            return result

                        except Exception as e:
                            span.set_attribute("error.type", type(e).__name__)
                            raise

                return cast(Callable[P, R], async_wrapper)

            @functools.wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                with self._start_decorated_as_current_span(
                    name=span_name,
                    func=func,
                    func_args=args,
                    kind=kind,
                    attributes=attributes,
                    baggage=baggage,
                    tags=tags,
                    label=label,
                    parent_context_id=parent_context_id,
                    trace_id=trace_id,
                    max_length=max_length,
                    func_type=function_type,
                    func_kwargs=kwargs,
                ) as span:
                    try:
                        result = func(*args, **kwargs)
                        span.set_output(result, max_length)
                        return result
                    except Exception as e:
                        span.set_attribute("error.type", type(e).__name__)
                        raise

            return cast(Callable[P, R], sync_wrapper)

        return decorator


def get_tracer(name: str) -> Tracer:
    """Get a Tracer instance by name.

    Args:
        name (str):
            The name of the tracer/service.
    """
    return Tracer(name)


class TracerProvider(_OtelTracerProvider):
    """
    Python wrapper around PyTracerProvider that returns Python Tracer instances.

    This wrapper ensures that get_tracer() returns the Python Tracer class
    with decorator support, not the Rust BaseTracer.
    """

    def __init__(
        self,
        transport_config: Optional[Any] = None,
        exporter: Optional[Any] = None,
        batch_config: Optional[BatchConfig] = None,
        sample_ratio: Optional[float] = None,
        scouter_queue: Optional[Any] = None,
    ):
        """Initialize TracerProvider and underlying Rust tracer."""

        self.transport_config = transport_config
        self.exporter = exporter
        self.batch_config = batch_config
        self.sample_ratio = sample_ratio
        self.scouter_queue = scouter_queue

    def get_tracer(
        self,
        instrumenting_module_name: str,
        instrumenting_library_version: Optional[str] = None,
        schema_url: Optional[str] = None,
        attributes: Optional[Attributes] = None,
    ) -> _OtelTracer:
        """
        Get a Python Tracer instance with decorator support.

        This method returns the Python Tracer class that wraps BaseTracer,
        providing the @tracer.span() decorator functionality.

        Args:
            instrumenting_module_name: Module name (typically __name__)
            instrumenting_library_version: Optional version string
            schema_url: Optional schema URL
            attributes: Optional attributes dict

        Returns:
            Tracer: Python Tracer instance with decorator support
        """
        # Return the Python Tracer wrapper, not the Rust BaseTracer

        return cast(
            _OtelTracer,
            init_tracer(
                service_name=instrumenting_module_name,
                scope=instrumenting_library_version,  # type: ignore
                transport_config=self.transport_config,
                exporter=self.exporter,
                batch_config=self.batch_config,
                sample_ratio=self.sample_ratio,
                scouter_queue=self.scouter_queue,
                schema_url=schema_url,
                attributes=attributes,  # type: ignore
            ),
        )

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush all pending spans."""
        flush_tracer()
        return True

    def shutdown(self) -> None:
        """Shutdown the tracer provider."""
        shutdown_tracer()


class ScouterInstrumentor(BaseInstrumentor):
    """
    OpenTelemetry-compatible instrumentor for Scouter tracing.

    Provides a standard instrument() interface that integrates with
    the OpenTelemetry SDK while using Scouter's Rust-based tracer.

    Examples:
        Basic usage:
        >>> from scouter.tracing import ScouterInstrumentor
        >>> from scouter import BatchConfig, GrpcConfig
        >>>
        >>> instrumentor = ScouterInstrumentor()
        >>> instrumentor.instrument(
        ...     transport_config=GrpcConfig(),
        ...     batch_config=BatchConfig(scheduled_delay_ms=200),
        ... )

        Auto-instrument on import:
        >>> from scouter.tracing import ScouterInstrumentor
        >>> ScouterInstrumentor().instrument()

        Cleanup:
        >>> instrumentor.uninstrument()
    """

    _instance: Optional["ScouterInstrumentor"] = None
    _provider: Optional[TracerProvider] = None

    def __new__(cls) -> "ScouterInstrumentor":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def instrumentation_dependencies(self) -> Collection[str]:
        """Return list of packages required for instrumentation."""
        return []

    def _instrument(self, **kwargs) -> None:
        """Initialize Scouter tracing and set as global provider."""
        if not HAS_OPENTELEMETRY:
            raise ImportError(
                "OpenTelemetry is required for instrumentation. "
                "Install with: pip install opsml[opentelemetry]"
            )

        if self._provider is not None:
            return

        tracer_provider = kwargs.pop("tracer_provider", None)

        if tracer_provider is not None:
            self._provider = tracer_provider
        else:
            self._provider = TracerProvider(
                transport_config=kwargs.pop("transport_config", None),
                exporter=kwargs.pop("exporter", None),
                batch_config=kwargs.pop("batch_config", None),
                sample_ratio=kwargs.pop("sample_ratio", None),
                scouter_queue=kwargs.pop("scouter_queue", None),
            )

        from opentelemetry import trace

        trace._TRACER_PROVIDER_SET_ONCE._done = False  # pylint: disable=protected-access
        trace._TRACER_PROVIDER_SET_ONCE._lock = __import__("threading").Lock()  # pylint: disable=protected-access
        set_tracer_provider(self._provider)

    def _uninstrument(self, **kwargs) -> None:
        """Shutdown Scouter tracing and reset global provider."""
        if not HAS_OPENTELEMETRY:
            return

        if self._provider is None:
            return

        self._provider.shutdown()

        from opentelemetry import trace

        trace._TRACER_PROVIDER = None  # pylint: disable=protected-access
        trace._TRACER_PROVIDER_SET_ONCE._done = False  # pylint: disable=protected-access

        self._provider = None

    @property
    def is_instrumented(self) -> bool:
        """Check if instrumentation is active."""
        return self._provider is not None


# Convenience function matching common pattern
def instrument(
    transport_config: Optional[Any] = None,
    exporter: Optional[Any] = None,
    batch_config: Optional[BatchConfig] = None,
    sample_ratio: Optional[float] = None,
    scouter_queue: Optional[Any] = None,
) -> None:
    """
    Convenience function to instrument with Scouter tracing.

    This is equivalent to:
        ScouterInstrumentor().instrument(**kwargs)

    Args:
        transport_config: Export configuration (OtelExportConfig, etc.)
        exporter: Custom span exporter instance
        batch_config: Batch processing configuration
        sample_ratio: Sampling ratio (0.0 to 1.0)
        scouter_queue: Optional ScouterQueue for buffering

    Examples:
        >>> from scouter.tracing import instrument
        >>> from scouter import BatchConfig, OtelExportConfig, OtelProtocol
        >>>
        >>> instrument(
        ...     transport_config=OtelExportConfig(
        ...         endpoint="http://localhost:4318/v1/traces",
        ...         protocol=OtelProtocol.HttpProtobuf,
        ...     ),
        ...     batch_config=BatchConfig(scheduled_delay_ms=200),
        ... )
    """
    ScouterInstrumentor().instrument(
        transport_config=transport_config,
        exporter=exporter,
        batch_config=batch_config,
        sample_ratio=sample_ratio,
        scouter_queue=scouter_queue,
    )


def uninstrument() -> None:
    """
    Convenience function to uninstrument Scouter tracing.

    This is equivalent to:
        ScouterInstrumentor().uninstrument()
    """
    ScouterInstrumentor().uninstrument()


__all__ = [
    "Tracer",
    "get_tracer",
    "init_tracer",
    "SpanKind",
    "FunctionType",
    "ActiveSpan",
    "OtelExportConfig",
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
    "get_tracing_headers_from_current_span",
    "get_current_active_span",
    "ScouterInstrumentor",
    "instrument",
    "uninstrument",
]
