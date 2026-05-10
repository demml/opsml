# pylint: disable=dangerous-default-value,implicit-str-concat
# mypy: disable-error-code="attr-defined"

import functools
import inspect
import threading
from contextlib import contextmanager
from types import TracebackType
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
    GrpcSpanExporter,
    HttpSpanExporter,
    OtelExportConfig,
    OtelProtocol,
    ScouterResourceConfig,
    SpanKind,
    StdoutSpanExporter,
    TestSpanExporter,
    TraceBaggageRecord,
    TraceFilters,
    TraceRecord,
    TraceSpanRecord,
    configure_tracing,
    disable_local_span_capture,
    drain_local_span_capture,
    enable_local_span_capture,
    extract_span_context_from_headers,
    flush_tracer,
    get_current_active_span,
    get_function_type,
)
from ..._opsml import get_tracer as _get_tracer
from ..._opsml import (
    get_tracing_headers_from_current_span,
    reset_tracer_provider,
    shutdown_tracer,
)
from .middleware import ScouterTracingMiddleware

SerializedType: TypeAlias = Union[str, int, float, dict, list]
P = ParamSpec("P")
R = TypeVar("R")
_OTEL_PROVIDER_RESET_LOCK = threading.Lock()
HAS_OPENTELEMETRY = True
if TYPE_CHECKING:
    from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
    from opentelemetry.trace import Span as _OtelSpan
    from opentelemetry.trace import Tracer as _OtelTracer
    from opentelemetry.trace import TracerProvider as _OtelTracerProvider
    from opentelemetry.trace import get_tracer_provider, set_tracer_provider
    from opentelemetry.util._decorator import _agnosticcontextmanager
    from opentelemetry.util.types import Attributes

    from ..._opsml import AgentEvalProfile
else:
    # Try to import OpenTelemetry, but provide fallbacks if not available
    try:
        from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
        from opentelemetry.trace import Span as _OtelSpan
        from opentelemetry.trace import Tracer as _OtelTracer
        from opentelemetry.trace import TracerProvider as _OtelTracerProvider
        from opentelemetry.trace import get_tracer_provider, set_tracer_provider
        from opentelemetry.util._decorator import _agnosticcontextmanager
        from opentelemetry.util.types import Attributes

        HAS_OPENTELEMETRY = True
    except ImportError:
        HAS_OPENTELEMETRY = False

        # Provide stub base class when OpenTelemetry is not installed
        class BaseInstrumentor:
            """Stub base class when OpenTelemetry is not available."""

            def instrument(self, **kwargs):
                raise ImportError("OpenTelemetry is not installed. Install with: " "pip install opsml[opentelemetry]")

            def uninstrument(self, **kwargs):
                raise ImportError("OpenTelemetry is not installed. Install with: " "pip install opsml[opentelemetry]")

        def get_tracer_provider():
            raise ImportError("OpenTelemetry is not installed. Install with: " "pip install opsml[opentelemetry]")

        def set_tracer_provider(provider):
            raise ImportError("OpenTelemetry is not installed. Install with: " "pip install opsml[opentelemetry]")

        _agnosticcontextmanager = contextmanager

        class _OtelTracerProvider:
            pass

        class _OtelTracer:
            pass

        class _OtelSpan:
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
    span: "ScouterSpan",
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


def _capture_arguments(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Mapping[str, Any]:
    try:
        bound = inspect.signature(func).bind(*args, **kwargs)
        bound.apply_defaults()
        return dict(bound.arguments)
    except Exception:  # noqa: BLE001 pylint: disable=broad-except
        return {"args": list(args), "kwargs": dict(kwargs)}


class ScouterSpan(_OtelSpan):
    """OTel-compliant span wrapper around the Rust ActiveSpan."""

    def __init__(self, active_span: ActiveSpan, name: str = ""):
        self._active = active_span
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        self._active.update_name(value)

    @property
    def trace_id(self) -> str:
        return self._active.trace_id

    @property
    def span_id(self) -> str:
        return self._active.span_id

    @property
    def context_id(self) -> str:
        return self._active.context_id

    @property
    def parent_context_id(self) -> Optional[str]:
        return self._active.parent_context_id

    def __enter__(self) -> "ScouterSpan":
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        del exc_type, exc_val, exc_tb
        self.end()

    async def __aenter__(self) -> "ScouterSpan":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        del exc_type, exc_val, exc_tb
        self.end()

    def get_span_context(self) -> Any:
        return self._active.get_span_context()

    def is_recording(self) -> bool:
        return self._active.is_recording()

    def set_status(self, status: Any, description: Optional[str] = None) -> None:
        resolved_description = description
        status_code = status
        if hasattr(status, "status_code"):
            status_code = status.status_code
            status_description = getattr(status, "description", None)
            if status_description and not resolved_description:
                resolved_description = status_description
        status_name = getattr(status_code, "name", str(status_code))
        self._active.set_status(status_name, resolved_description)

    def set_attribute(self, key: str, value: Any) -> None:
        self._active.set_attribute(key, value)

    def set_attributes(self, attributes: Mapping[str, Any]) -> None:
        self._active.set_attributes(dict(attributes))

    def add_event(
        self,
        name: str,
        attributes: Optional[Mapping[str, Any]] = None,
        timestamp: Optional[int] = None,
    ) -> None:
        active_attributes = dict(attributes) if attributes is not None else {}
        self._active.add_event(name, active_attributes, timestamp)

    def add_link(
        self,
        context: Any,
        attributes: Optional[Mapping[str, Any]] = None,
    ) -> None:
        active_attributes = dict(attributes) if isinstance(attributes, Mapping) else attributes
        self._active.add_link(context, active_attributes)

    def update_name(self, name: str) -> None:
        self._name = name
        self._active.update_name(name)

    def end(self, end_time: Optional[int] = None) -> None:
        self._active.end(end_time)

    def record_exception(
        self,
        exception: BaseException,
        attributes: Optional[Mapping[str, Any]] = None,
        timestamp: Optional[int] = None,
        escaped: bool = False,
    ) -> None:
        active_exception = exception if isinstance(exception, Exception) else Exception(str(exception))
        active_attributes = dict(attributes) if isinstance(attributes, Mapping) else attributes
        self._active.record_exception(active_exception, active_attributes, timestamp, escaped)

    # Scouter-specific extensions
    def set_input(self, value: Any, max_length: int = 1000) -> None:
        self._active.set_input(value, max_length)

    def set_output(self, value: Any, max_length: int = 1000) -> None:
        self._active.set_output(value, max_length)

    def set_tag(self, key: str, value: Any) -> None:
        self._active.set_tag(key, value)

    def attach_eval(
        self,
        profile_uid: str,
        context: Any,
        *,
        record_id: Optional[str] = None,
        session_id: Optional[str] = None,
        media: Optional[list[Any]] = None,
        tags: Optional[list[str]] = None,
    ) -> None:
        """Attach an eval record to this span's trace.

        `profile_uid` is the target AgentEvalProfile UID. `context` accepts the
        same dict or Pydantic model payloads as EvalRecord. `record_id` is a
        caller-defined scenario, turn, step, or callback ID, not the database
        row ID. `session_id`, `media`, and `tags` are preserved on the created
        EvalRecord. If this trace is not sampled, no eval record is inserted.
        """
        self._active.attach_eval(
            profile_uid,
            context,
            record_id=record_id,
            session_id=session_id,
            media=media,
            tags=tags,
        )

    @property
    def active_span(self) -> ActiveSpan:
        return self._active


class ScouterTracer(_OtelTracer):
    """OTel-compliant tracer wrapping the Rust BaseTracer."""

    def __init__(self, base_tracer: BaseTracer):
        self._base = base_tracer

    @staticmethod
    def _normalize_attributes(attributes: Optional[Any]) -> Optional[Any]:
        if attributes is None:
            return None
        if isinstance(attributes, Mapping):
            return dict(attributes)
        return attributes

    @staticmethod
    def _apply_baggage_to_context(
        baggage: Optional[List[dict[str, str]]],
        context: Optional[Any],
    ) -> Optional[Any]:
        if not baggage or not HAS_OPENTELEMETRY:
            return context
        from opentelemetry import baggage as otel_baggage
        from opentelemetry import context as otel_context_api

        target = context if context is not None else otel_context_api.get_current()
        for item in baggage:
            for k, v in item.items():
                target = otel_baggage.set_baggage(k, str(v), target)
        return target

    @staticmethod
    def _resolve_parent_context_id(context: Optional[Any]) -> Optional[str]:
        if not HAS_OPENTELEMETRY:
            return None
        from opentelemetry import trace

        parent_span = trace.get_current_span(context)
        if isinstance(parent_span, ScouterSpan) and parent_span.is_recording():
            return parent_span.context_id
        return None

    def start_span(
        self,
        name: str,
        context: Optional[Any] = None,
        kind: Any = SpanKind.Internal,
        attributes: Optional[Any] = None,
        links: Optional[Any] = None,
        start_time: Optional[int] = None,
        record_exception: bool = True,
        set_status_on_exception: bool = True,
        baggage: Optional[List[dict[str, str]]] = None,
        tags: Optional[List[dict[str, str]]] = None,
        label: Optional[str] = None,
        parent_context_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        remote_sampled: Optional[bool] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> ScouterSpan:
        current_context = context
        if baggage:
            current_context = self._apply_baggage_to_context(baggage, current_context)
        resolved_parent_context_id = parent_context_id or self._resolve_parent_context_id(current_context)

        active = self._base.start_span(
            name=name,
            context=current_context,
            kind=kind,
            attributes=self._normalize_attributes(attributes),
            baggage=baggage or [],
            tags=tags or [],
            label=label,
            parent_context_id=resolved_parent_context_id,
            trace_id=trace_id,
            span_id=span_id,
            remote_sampled=remote_sampled,
            headers=headers,
            links=links,
            start_time=start_time,
            record_exception=record_exception,
            set_status_on_exception=set_status_on_exception,
        )
        return ScouterSpan(active, name=name)

    @_agnosticcontextmanager
    def start_as_current_span(  # type: ignore[override]
        self,
        name: str,
        context: Optional[Any] = None,
        kind: Any = SpanKind.Internal,
        attributes: Optional[Any] = None,
        links: Optional[Any] = None,
        start_time: Optional[int] = None,
        record_exception: bool = True,
        set_status_on_exception: bool = True,
        end_on_exit: bool = True,
        baggage: Optional[List[dict[str, str]]] = None,
        tags: Optional[List[dict[str, str]]] = None,
        label: Optional[str] = None,
        parent_context_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        remote_sampled: Optional[bool] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Generator[ScouterSpan, None, None]:
        # Build enriched context with baggage before creating span
        enriched_ctx = context
        if baggage:
            enriched_ctx = self._apply_baggage_to_context(baggage, enriched_ctx)

        span = self.start_span(
            name=name,
            context=enriched_ctx,
            kind=kind,
            attributes=attributes,
            links=links,
            start_time=start_time,
            record_exception=record_exception,
            set_status_on_exception=set_status_on_exception,
            baggage=None,
            tags=tags,
            label=label,
            parent_context_id=parent_context_id,
            trace_id=trace_id,
            span_id=span_id,
            remote_sampled=remote_sampled,
            headers=headers,
        )

        if HAS_OPENTELEMETRY:
            from opentelemetry import context as otel_ctx_api
            from opentelemetry import trace

            # Attach baggage-enriched context so use_span derives from it,
            # making baggage visible to all child spans in Python contextvars.
            baggage_token = otel_ctx_api.attach(enriched_ctx) if baggage and enriched_ctx is not None else None
            try:
                with trace.use_span(  # pylint: disable=not-context-manager
                    span,
                    end_on_exit=end_on_exit,
                    record_exception=record_exception,
                    set_status_on_exception=set_status_on_exception,
                ) as active:
                    yield cast(ScouterSpan, active)
            finally:
                if baggage_token is not None:
                    otel_ctx_api.detach(baggage_token)
            return

        try:
            yield span
        finally:
            if end_on_exit:
                span.end()

    def span(
        self,
        name: Optional[str] = None,
        kind: Any = SpanKind.Internal,
        attributes: List[dict[str, str]] = [],
        baggage: List[dict[str, str]] = [],
        tags: List[dict[str, str]] = [],
        label: Optional[str] = None,
        parent_context_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        max_length: int = 1000,
        capture_last_stream_item: bool = False,
        join_stream_items: bool = False,
        **_kwargs,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            span_name = name or f"{func.__module__}.{getattr(func, '__qualname__', repr(func))}"
            function_type = get_function_type(func)

            if function_type == FunctionType.AsyncGenerator:

                @functools.wraps(func)
                async def async_generator_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                    with self.start_as_current_span(
                        name=span_name,
                        kind=kind,
                        attributes=attributes,
                        baggage=baggage,
                        tags=tags,
                        label=label,
                        parent_context_id=parent_context_id,
                        trace_id=trace_id,
                    ) as span:
                        span.set_input(_capture_arguments(func, args, kwargs), max_length)
                        async_gen_func = cast(Callable[P, AsyncGenerator[Any, None]], func)
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

                return cast(Callable[P, R], async_generator_wrapper)

            if function_type == FunctionType.SyncGenerator:

                @functools.wraps(func)
                def generator_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                    with self.start_as_current_span(
                        name=span_name,
                        kind=kind,
                        attributes=attributes,
                        baggage=baggage,
                        tags=tags,
                        label=label,
                        parent_context_id=parent_context_id,
                        trace_id=trace_id,
                    ) as span:
                        span.set_input(_capture_arguments(func, args, kwargs), max_length)
                        gen_func = cast(Callable[P, Generator[Any, None, None]], func)
                        generator = gen_func(*args, **kwargs)
                        outputs = []

                        for item in generator:
                            outputs.append(item)
                            yield item

                        set_output(
                            span,
                            outputs,
                            max_length,
                            capture_last_stream_item,
                            join_stream_items,
                        )

                return cast(Callable[P, R], generator_wrapper)

            if function_type == FunctionType.Async:

                @functools.wraps(func)
                async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                    with self.start_as_current_span(
                        name=span_name,
                        kind=kind,
                        attributes=attributes,
                        baggage=baggage,
                        tags=tags,
                        label=label,
                        parent_context_id=parent_context_id,
                        trace_id=trace_id,
                    ) as span:
                        span.set_input(_capture_arguments(func, args, kwargs), max_length)
                        async_func = cast(Callable[P, Awaitable[Any]], func)
                        result = await async_func(*args, **kwargs)
                        span.set_output(result, max_length)
                        return result

                return cast(Callable[P, R], async_wrapper)

            @functools.wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                with self.start_as_current_span(
                    name=span_name,
                    kind=kind,
                    attributes=attributes,
                    baggage=baggage,
                    tags=tags,
                    label=label,
                    parent_context_id=parent_context_id,
                    trace_id=trace_id,
                ) as span:
                    span.set_input(_capture_arguments(func, args, kwargs), max_length)
                    result = func(*args, **kwargs)
                    span.set_output(result, max_length)
                    return result

            return cast(Callable[P, R], sync_wrapper)

        return decorator

    @property
    def current_span(self) -> ScouterSpan:
        return ScouterSpan(self._base.current_span, name="")

    @property
    def base_tracer(self) -> BaseTracer:
        return self._base

    def set_scouter_queue(self, queue: Any) -> None:
        self._base.set_scouter_queue(queue)

    def shutdown(self) -> None:
        self._base.shutdown()

    def enable_local_capture(self, capture_run_id: str) -> None:
        self._base.enable_local_capture(capture_run_id)

    def disable_local_capture(self, capture_run_id: str) -> None:
        self._base.disable_local_capture(capture_run_id)

    def drain_local_spans(self, capture_run_id: str) -> List[TraceSpanRecord]:
        return self._base.drain_local_spans(capture_run_id)

    def get_local_spans_by_trace_ids(self, capture_run_id: str, trace_ids: List[str]) -> List[TraceSpanRecord]:
        return self._base.get_local_spans_by_trace_ids(capture_run_id, trace_ids)


def get_tracer(
    name: str,
    version: Optional[str] = None,
    schema_url: Optional[str] = None,
    attributes: Optional[Attributes] = None,
    default_attributes: Optional[Attributes] = None,
    scouter_queue: Optional[Any] = None,
) -> ScouterTracer:
    """Return an OTel-compliant Scouter tracer for an instrumentation scope.

    The `name` and optional `version` arguments become the OpenTelemetry
    InstrumentationScope name and version. They are intentionally independent of
    the process-wide Resource `service.name`, which is configured through
    `ScouterInstrumentor.instrument(service_name=...)` or environment variables.

    Args:
        name:
            Name of the instrumenting library or module, for example "httpx",
            "fastapi", or "opsml.agent".
        version:
            Optional version for the instrumenting library or module.
        schema_url:
            Optional OpenTelemetry schema URL associated with the scope.
        attributes:
            Optional attributes attached to the InstrumentationScope.
        default_attributes:
            Optional attributes applied to every span created by this tracer.
            Passing this creates a fresh low-level tracer wrapper even when a
            provider-level tracer is cached.
        scouter_queue:
            Optional queue used by ``span.attach_eval(...)``. Passing this
            creates a fresh low-level tracer wrapper so queue state is bound to
            the returned tracer.

    Returns:
        A `ScouterTracer` wrapper for the requested instrumentation scope.
    """
    if not HAS_OPENTELEMETRY:
        raise ImportError("OpenTelemetry is not installed. Install with: pip install opsml[opentelemetry]")

    if default_attributes is not None or scouter_queue is not None:
        return ScouterTracer(
            _get_tracer(
                scope_name=name,
                scope_version=version,
                schema_url=schema_url,
                scope_attributes=cast(Optional[dict[str, Any]], attributes),
                default_attributes=cast(Optional[dict[str, Any]], default_attributes),
                scouter_queue=scouter_queue,
            )
        )

    provider = get_tracer_provider()
    tracer = provider.get_tracer(name, version, schema_url, attributes)
    if isinstance(tracer, ScouterTracer):
        return tracer

    try:
        return ScouterTracer(
            _get_tracer(
                scope_name=name,
                scope_version=version,
                schema_url=schema_url,
                scope_attributes=cast(Optional[dict[str, Any]], attributes),
            )
        )
    except Exception as exc:  # noqa: BLE001 pylint: disable=broad-except
        raise RuntimeError("ScouterInstrumentor.instrument() must be called before get_tracer()") from exc


class ScouterTracerProvider(_OtelTracerProvider):
    """OTel-compliant tracer provider returning ScouterTracer instances."""

    def __init__(
        self,
        resource_config: Optional["ScouterResourceConfig"] = None,
        transport_config: Optional[Any] = None,
        exporter: Optional[Any] = None,
        batch_config: Optional[BatchConfig] = None,
        sample_ratio: Optional[float] = None,
        scouter_queue: Optional[Any] = None,
        default_attributes: Optional[Attributes] = None,
    ):
        """Initialize the provider and configure the Rust tracing backend.

        Args:
            resource_config:
                Optional process Resource configuration. If omitted, Scouter
                derives service identity from OTEL_SERVICE_NAME,
                OTEL_RESOURCE_ATTRIBUTES, and defaults.
            transport_config:
                Optional Scouter transport configuration.
            exporter:
                Optional secondary OTEL exporter.
            batch_config:
                Optional batch span processor settings.
            sample_ratio:
                Optional trace sampling ratio in [0.0, 1.0].
            scouter_queue:
                Optional queue attached to tracers returned by this provider.
            default_attributes:
                Optional attributes applied to every span created by provider
                tracers.
        """
        self.resource_config = resource_config
        self.transport_config = transport_config
        self.exporter = exporter
        self.batch_config = batch_config
        self.sample_ratio = sample_ratio
        self.scouter_queue = scouter_queue
        self.default_attributes = default_attributes
        self._tracer_cache: dict[
            tuple[str, str | None, str | None],
            ScouterTracer,
        ] = {}
        self._tracer_cache_lock = threading.Lock()

        configure_tracing(
            resource_config=resource_config,
            transport_config=transport_config,
            exporter=exporter,
            batch_config=batch_config,
            sample_ratio=sample_ratio,
        )

    def get_tracer(
        self,
        instrumenting_module_name: str,
        instrumenting_library_version: Optional[str] = None,
        schema_url: Optional[str] = None,
        attributes: Optional[Attributes] = None,
    ) -> ScouterTracer:
        """Return a cached Scouter tracer for an instrumentation scope.

        Args:
            instrumenting_module_name:
                Name of the instrumenting library or module.
            instrumenting_library_version:
                Optional version of the instrumenting library or module.
            schema_url:
                Optional OpenTelemetry schema URL associated with the scope.
            attributes:
                Optional attributes attached to the InstrumentationScope.

        Returns:
            A cached `ScouterTracer` for the requested scope.
        """

        cache_key = (
            instrumenting_module_name,
            instrumenting_library_version,
            schema_url,
        )
        if cache_key in self._tracer_cache:
            return self._tracer_cache[cache_key]

        with self._tracer_cache_lock:
            if cache_key in self._tracer_cache:
                return self._tracer_cache[cache_key]

            base_tracer = _get_tracer(
                scope_name=instrumenting_module_name,
                scope_version=instrumenting_library_version,
                schema_url=schema_url,
                scope_attributes=attributes,  # type: ignore
                default_attributes=self.default_attributes,  # type: ignore
                scouter_queue=self.scouter_queue,
            )
            tracer = ScouterTracer(base_tracer)
            self._tracer_cache[cache_key] = tracer
            return tracer

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush all pending spans."""
        flush_tracer()
        return True

    def shutdown(self) -> None:
        """Shutdown the tracer provider."""
        with self._tracer_cache_lock:
            self._tracer_cache.clear()
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
    _provider: Optional[ScouterTracerProvider] = None

    def __new__(cls) -> "ScouterInstrumentor":
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        pass

    def instrumentation_dependencies(self) -> Collection[str]:
        """Return list of packages required for instrumentation."""
        return []

    def _instrument(self, **kwargs) -> None:
        """Initialize Scouter tracing and set as global provider."""
        if not HAS_OPENTELEMETRY:
            raise ImportError(
                "OpenTelemetry is required for instrumentation. " "Install with: pip install opsml[opentelemetry]"
            )

        if self._provider is not None:
            import logging

            logging.getLogger("scouter.tracing").warning(
                "ScouterInstrumentor is already instrumented. "
                "ScouterInstrumentor is process-wide — call uninstrument() first to reconfigure. "
                "The existing provider will be used."
            )
            return

        kwargs.pop("eval_profiles", None)

        tracer_provider = kwargs.pop("tracer_provider", None)

        if tracer_provider is not None:
            self._provider = tracer_provider
        else:
            resource_config = kwargs.pop("resource_config", None)
            if resource_config is None:
                resource_config = ScouterResourceConfig(
                    service_name=kwargs.pop("service_name", None),
                    service_version=kwargs.pop("service_version", None),
                    service_namespace=kwargs.pop("service_namespace", None),
                    service_instance_id=kwargs.pop("service_instance_id", None),
                    extra_attributes=kwargs.pop("resource_attributes", None) or {},
                )
            else:
                for k in (
                    "service_name",
                    "service_version",
                    "service_namespace",
                    "service_instance_id",
                    "resource_attributes",
                ):
                    kwargs.pop(k, None)

            self._provider = ScouterTracerProvider(
                resource_config=resource_config,
                transport_config=kwargs.pop("transport_config", None),
                exporter=kwargs.pop("exporter", None),
                batch_config=kwargs.pop("batch_config", None),
                sample_ratio=kwargs.pop("sample_ratio", None),
                scouter_queue=kwargs.pop("scouter_queue", None),
                default_attributes=kwargs.pop("attributes", None),
            )

        from opentelemetry import trace

        with _OTEL_PROVIDER_RESET_LOCK:
            try:
                trace._TRACER_PROVIDER_SET_ONCE._done = False  # pylint: disable=protected-access
                trace._TRACER_PROVIDER_SET_ONCE._lock = threading.Lock()  # pylint: disable=protected-access
            except AttributeError:
                import logging as _logging

                _logging.getLogger("scouter.tracing").warning(
                    "Could not reset OTel provider guard — opentelemetry-api internals may have "
                    "changed. Proceeding anyway."
                )
            set_tracer_provider(self._provider)

        propagate_baggage = kwargs.pop("propagate_baggage", True)

        # Register W3C TraceContext + Baggage propagators so that third-party
        # instrumentors (StarletteInstrumentor, HTTPXInstrumentor, etc.) can
        # inject and extract traceparent/tracestate headers transparently.
        try:
            from opentelemetry.propagate import set_global_textmap
            from opentelemetry.propagators.composite import CompositePropagator
            from opentelemetry.trace.propagation.tracecontext import (
                TraceContextTextMapPropagator,
            )

            if propagate_baggage:
                from opentelemetry.baggage.propagation import W3CBaggagePropagator

                set_global_textmap(
                    CompositePropagator(
                        [
                            TraceContextTextMapPropagator(),
                            W3CBaggagePropagator(),
                        ]
                    )
                )
            else:
                set_global_textmap(
                    CompositePropagator(
                        [
                            TraceContextTextMapPropagator(),
                        ]
                    )
                )
        except ImportError:
            pass  # opentelemetry-api not fully installed; propagator setup skipped

    def instrument(
        self,
        service_name: Optional[str] = None,
        service_version: Optional[str] = None,
        service_namespace: Optional[str] = None,
        service_instance_id: Optional[str] = None,
        resource_attributes: Optional[dict[str, str]] = None,
        resource_config: Optional["ScouterResourceConfig"] = None,
        transport_config: Optional[Any] = None,
        exporter: Optional[Any] = None,
        batch_config: Optional[BatchConfig] = None,
        sample_ratio: Optional[float] = None,
        scouter_queue: Optional[Any] = None,
        attributes: Optional[Attributes] = None,
        eval_profiles: Optional[List["AgentEvalProfile"]] = None,
        propagate_baggage: bool = True,
        **kwargs,
    ) -> None:
        """
        Instrument with Scouter tracing.

        OTel resolution precedence (per spec):
            explicit kwargs > OTEL_SERVICE_NAME > OTEL_RESOURCE_ATTRIBUTES > "unknown_service"
        """
        super().instrument(
            service_name=service_name,
            service_version=service_version,
            service_namespace=service_namespace,
            service_instance_id=service_instance_id,
            resource_attributes=resource_attributes,
            resource_config=resource_config,
            transport_config=transport_config,
            exporter=exporter,
            batch_config=batch_config,
            sample_ratio=sample_ratio,
            scouter_queue=scouter_queue,
            attributes=attributes,
            eval_profiles=eval_profiles,
            propagate_baggage=propagate_baggage,
            **kwargs,
        )

    def enable_local_capture(self, capture_run_id: str) -> None:
        """Enable local span capture mode for a capture run."""
        get_tracer("scouter").enable_local_capture(capture_run_id)

    def disable_local_capture(self, capture_run_id: str) -> None:
        """Disable local span capture mode for a capture run."""
        get_tracer("scouter").disable_local_capture(capture_run_id)

    def drain_local_spans(self, capture_run_id: str) -> List[TraceSpanRecord]:
        """Drain and return locally captured spans for a capture run."""
        return get_tracer("scouter").drain_local_spans(capture_run_id)

    def get_local_spans_by_trace_ids(self, capture_run_id: str, trace_ids: List[str]) -> List[TraceSpanRecord]:
        """Return captured spans matching the given trace IDs without draining the run buffer."""
        return get_tracer("scouter").get_local_spans_by_trace_ids(capture_run_id, trace_ids)

    def _uninstrument(self, **kwargs) -> None:
        """Shutdown Scouter tracing and reset global provider."""
        if not HAS_OPENTELEMETRY:
            return

        if self._provider is not None:
            self._provider.shutdown()
            self._provider = None
        else:
            try:
                flush_tracer()
            except Exception:  # noqa: BLE001 pylint: disable=broad-except
                pass
            try:
                shutdown_tracer()
            except Exception:  # noqa: BLE001 pylint: disable=broad-except
                pass

        from opentelemetry import trace

        try:
            trace._TRACER_PROVIDER = None  # pylint: disable=protected-access
            trace._TRACER_PROVIDER_SET_ONCE._done = False  # pylint: disable=protected-access
        except AttributeError:
            pass

        # Reset the singleton
        ScouterInstrumentor._instance = None

        assert self._provider is None, "Expected provider to be None after uninstrument()"

    @property
    def is_instrumented(self) -> bool:
        """Check if instrumentation is active."""
        return self._provider is not None


# Convenience function matching common pattern
def instrument(
    service_name: Optional[str] = None,
    service_version: Optional[str] = None,
    service_namespace: Optional[str] = None,
    service_instance_id: Optional[str] = None,
    resource_attributes: Optional[dict[str, str]] = None,
    resource_config: Optional["ScouterResourceConfig"] = None,
    transport_config: Optional[Any] = None,
    exporter: Optional[Any] = None,
    batch_config: Optional[BatchConfig] = None,
    sample_ratio: Optional[float] = None,
    scouter_queue: Optional[Any] = None,
    attributes: Optional[Attributes] = None,
    eval_profiles: Optional[List["AgentEvalProfile"]] = None,
    propagate_baggage: bool = True,
) -> None:
    """
    Convenience function to instrument with Scouter tracing.

    This is equivalent to:
        ScouterInstrumentor().instrument(**kwargs)

    Args:
        service_name (Optional[str]):
            Explicit process-wide `service.name` Resource attribute.
        service_version (Optional[str]):
            Explicit process-wide `service.version` Resource attribute.
        service_namespace (Optional[str]):
            Explicit process-wide `service.namespace` Resource attribute.
        service_instance_id (Optional[str]):
            Explicit process-wide `service.instance.id` Resource attribute.
        resource_attributes (Optional[dict[str, str]]):
            Additional process-wide Resource attributes.
        resource_config (Optional[ScouterResourceConfig]):
            Prebuilt Resource configuration. When provided, individual
            service/resource kwargs are ignored.
        transport_config (Optional[Any]):
            Export configuration (OtelExportConfig, etc.)
        exporter (Optional[Any]):
            Custom span exporter instance
        batch_config (Optional[BatchConfig]):
            Batch processing configuration
        sample_ratio (Optional[float]):
            Sampling ratio (0.0 to 1.0)
        scouter_queue (Optional[Any]):
            Optional ScouterQueue for buffering
        attributes (Optional[Attributes]):
            Optional attributes to set on every span created by this tracer
        eval_profiles (Optional[List[AgentEvalProfile]]):
            Deprecated no-op retained for call-site compatibility. Use
            ``span.attach_eval(profile_uid=...)`` to attach eval records to a
            trace.
        propagate_baggage (bool):
            Whether W3C baggage propagation should be globally enabled.

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
        service_name=service_name,
        service_version=service_version,
        service_namespace=service_namespace,
        service_instance_id=service_instance_id,
        resource_attributes=resource_attributes,
        resource_config=resource_config,
        transport_config=transport_config,
        exporter=exporter,
        batch_config=batch_config,
        sample_ratio=sample_ratio,
        scouter_queue=scouter_queue,
        attributes=attributes,
        eval_profiles=eval_profiles,
        propagate_baggage=propagate_baggage,
    )


def uninstrument() -> None:
    """
    Convenience function to uninstrument Scouter tracing.

    This is equivalent to:
        ScouterInstrumentor().uninstrument()
    """
    ScouterInstrumentor().uninstrument()


__all__ = [
    "ScouterSpan",
    "ScouterTracer",
    "ScouterTracerProvider",
    "get_tracer",
    "configure_tracing",
    "ScouterResourceConfig",
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
    "TraceFilters",
    "TestSpanExporter",
    "flush_tracer",
    "BatchConfig",
    "shutdown_tracer",
    "reset_tracer_provider",
    "get_tracing_headers_from_current_span",
    "extract_span_context_from_headers",
    "get_current_active_span",
    "ScouterInstrumentor",
    "ScouterTracingMiddleware",
    "instrument",
    "uninstrument",
    "enable_local_span_capture",
    "disable_local_span_capture",
    "drain_local_span_capture",
]
