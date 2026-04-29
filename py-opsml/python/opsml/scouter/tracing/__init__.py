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
    SpanKind,
    StdoutSpanExporter,
    TestSpanExporter,
    TraceBaggageRecord,
    TraceRecord,
    TraceSpanRecord,
    disable_local_span_capture,
    drain_local_span_capture,
    enable_local_span_capture,
    extract_span_context_from_headers,
    flush_tracer,
    get_current_active_span,
    get_function_type,
    get_tracing_headers_from_current_span,
    init_tracer,
    shutdown_tracer,
)
from .middleware import ScouterTracingMiddleware

SerializedType: TypeAlias = Union[str, int, float, dict, list]
P = ParamSpec("P")
R = TypeVar("R")
SCOUTER_ACTIVE_ENTITY_UID_BAGGAGE_KEY = "scouter.active.entity_uid"
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

    def set_entity(self, entity_id: str) -> None:
        self._active.set_entity(entity_id)

    def set_tag(self, key: str, value: Any) -> None:
        self._active.set_tag(key, value)

    def add_queue_item(self, alias: str, item: Any) -> None:
        self._active.add_queue_item(alias, item)

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
    def _current_context(context: Optional[Any]) -> Optional[Any]:
        if context is not None:
            return context
        if not HAS_OPENTELEMETRY:
            return None
        from opentelemetry import context as context_api

        return context_api.get_current()

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
        current_context = self._current_context(context)
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
        span = self.start_span(
            name=name,
            context=context,
            kind=kind,
            attributes=attributes,
            links=links,
            start_time=start_time,
            record_exception=record_exception,
            set_status_on_exception=set_status_on_exception,
            baggage=baggage,
            tags=tags,
            label=label,
            parent_context_id=parent_context_id,
            trace_id=trace_id,
            span_id=span_id,
            remote_sampled=remote_sampled,
            headers=headers,
        )

        if HAS_OPENTELEMETRY:
            from opentelemetry import trace

            with trace.use_span(  # pylint: disable=not-context-manager
                span,
                end_on_exit=end_on_exit,
                record_exception=record_exception,
                set_status_on_exception=set_status_on_exception,
            ) as active:
                yield cast(ScouterSpan, active)
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

    def enable_local_capture(self) -> None:
        self._base.enable_local_capture()

    def disable_local_capture(self) -> None:
        self._base.disable_local_capture()

    def drain_local_spans(self) -> List[TraceSpanRecord]:
        return self._base.drain_local_spans()

    def get_local_spans_by_trace_ids(self, trace_ids: List[str]) -> List[TraceSpanRecord]:
        return self._base.get_local_spans_by_trace_ids(trace_ids)


def get_tracer(name: str) -> ScouterTracer:
    """Get an OTel-compliant Scouter tracer."""
    if not HAS_OPENTELEMETRY:
        try:
            return ScouterTracer(BaseTracer(name))
        except Exception as exc:  # noqa: BLE001 pylint: disable=broad-except
            raise RuntimeError(
                "init_tracer() must be called before get_tracer() when OpenTelemetry is unavailable"
            ) from exc

    provider = get_tracer_provider()
    tracer = provider.get_tracer(name)
    if isinstance(tracer, ScouterTracer):
        return tracer

    # init_tracer() path: provider may not be ScouterTracerProvider, but the
    # Rust tracer provider store is initialized and can still construct a valid
    # ScouterTracer wrapper.
    try:
        return ScouterTracer(BaseTracer(name))
    except Exception as exc:  # noqa: BLE001 pylint: disable=broad-except
        raise RuntimeError(
            "ScouterInstrumentor.instrument() or init_tracer() must be called before get_tracer()"
        ) from exc


class ScouterTracerProvider(_OtelTracerProvider):
    """OTel tracer provider returning ScouterTracer instances."""

    def __init__(
        self,
        transport_config: Optional[Any] = None,
        exporter: Optional[Any] = None,
        batch_config: Optional[BatchConfig] = None,
        sample_ratio: Optional[float] = None,
        scouter_queue: Optional[Any] = None,
        default_attributes: Optional[Attributes] = None,
        default_entity_uid: Optional[str] = None,
    ):
        """Initialize ScouterTracerProvider and underlying Rust tracer."""

        self.transport_config = transport_config
        self.exporter = exporter
        self.batch_config = batch_config
        self.sample_ratio = sample_ratio
        self.scouter_queue = scouter_queue
        self.default_attributes = default_attributes
        self.default_entity_uid = default_entity_uid
        self._tracer_cache: dict[
            tuple[str, str | None, str | None],
            ScouterTracer,
        ] = {}
        self._tracer_cache_lock = threading.Lock()

    def get_tracer(
        self,
        instrumenting_module_name: str,
        instrumenting_library_version: Optional[str] = None,
        schema_url: Optional[str] = None,
        attributes: Optional[Attributes] = None,
    ) -> ScouterTracer:
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

            base_tracer = init_tracer(
                service_name=instrumenting_module_name,
                scope=instrumenting_library_version,  # type: ignore
                transport_config=self.transport_config,
                exporter=self.exporter,
                batch_config=self.batch_config,
                sample_ratio=self.sample_ratio,
                scouter_queue=self.scouter_queue,
                schema_url=schema_url,
                scope_attributes=attributes,  # type: ignore
                default_attributes=self.default_attributes,  # type: ignore
                default_entity_uid=self.default_entity_uid,
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

        eval_profiles: Optional[List["AgentEvalProfile"]] = kwargs.pop("eval_profiles", None)
        if eval_profiles:
            kwargs["default_entity_uid"] = eval_profiles[0].config.uid

        tracer_provider = kwargs.pop("tracer_provider", None)

        if tracer_provider is not None:
            self._provider = tracer_provider
        else:
            self._provider = ScouterTracerProvider(
                transport_config=kwargs.pop("transport_config", None),
                exporter=kwargs.pop("exporter", None),
                batch_config=kwargs.pop("batch_config", None),
                sample_ratio=kwargs.pop("sample_ratio", None),
                scouter_queue=kwargs.pop("scouter_queue", None),
                default_attributes=kwargs.pop("attributes", None),
                default_entity_uid=kwargs.pop("default_entity_uid", None),
            )

        from opentelemetry import trace

        try:
            trace._TRACER_PROVIDER_SET_ONCE._done = False  # pylint: disable=protected-access
            trace._TRACER_PROVIDER_SET_ONCE._lock = __import__("threading").Lock()  # pylint: disable=protected-access
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
        Instrument with Scouter tracing and set as global OpenTelemetry provider.

        Args:
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
                Optional agent eval profiles. The first profile UID becomes the
                default entity tag materialized on each span as
                `scouter.entity.{uid}={uid}` unless overridden by
                `active_profile(...)`.
            propagate_baggage (bool):
                Whether W3C baggage propagation should be globally enabled.
            **kwargs:
                Additional keyword arguments for ScouterTracerProvider initialization

        """
        super().instrument(
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

    def enable_local_capture(self) -> None:
        """Enable local span capture mode on the ScouterSpanExporter."""
        get_tracer("scouter").enable_local_capture()

    def disable_local_capture(self) -> None:
        """Disable local span capture mode, discarding any buffered spans."""
        get_tracer("scouter").disable_local_capture()

    def drain_local_spans(self) -> List[TraceSpanRecord]:
        """Drain and return all locally captured spans, clearing the buffer."""
        return get_tracer("scouter").drain_local_spans()

    def get_local_spans_by_trace_ids(self, trace_ids: List[str]) -> List[TraceSpanRecord]:
        """Return captured spans matching the given trace IDs without draining the buffer."""
        return get_tracer("scouter").get_local_spans_by_trace_ids(trace_ids)

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
            Optional agent eval profiles. The first profile UID becomes the
            default entity tag materialized on each span as
            `scouter.entity.{uid}={uid}` unless overridden by
            `active_profile(...)`.
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


@contextmanager
def active_profile(profile: "AgentEvalProfile") -> Generator[None, None, None]:
    """Set the active agent eval profile UID in OTel baggage context.

    This context manager attaches the profile UID as OTel baggage under the
    canonical key ``scouter.active.entity_uid``. Rust span creation reads this
    baggage value and materializes the authoritative span attribute
    ``scouter.entity.{profile.config.uid}={profile.config.uid}``.

    If ``opentelemetry`` is not installed, the context manager is a no-op.

    Args:
        profile (AgentEvalProfile):
            The agent eval profile to activate.
    """
    try:
        from opentelemetry import baggage
        from opentelemetry import context as context_api
    except ImportError:
        yield
        return

    ctx = baggage.set_baggage(
        SCOUTER_ACTIVE_ENTITY_UID_BAGGAGE_KEY,
        profile.config.uid,
        context=context_api.get_current(),
    )
    token = context_api.attach(ctx)
    try:
        yield
    finally:
        context_api.detach(token)


__all__ = [
    "ScouterSpan",
    "ScouterTracer",
    "ScouterTracerProvider",
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
    "extract_span_context_from_headers",
    "get_current_active_span",
    "ScouterInstrumentor",
    "ScouterTracingMiddleware",
    "instrument",
    "uninstrument",
    "active_profile",
    "enable_local_span_capture",
    "disable_local_span_capture",
    "drain_local_span_capture",
]
