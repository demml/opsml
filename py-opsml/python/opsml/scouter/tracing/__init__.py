# mypy: disable-error-code="attr-defined"
# pylint: disable=dangerous-default-value
import functools
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Generator,
    List,
    Optional,
    ParamSpec,
    TypeVar,
    cast,
)

from ..._opsml import (
    ActiveSpan,
    BaseTracer,
    BatchConfig,
    CompressionType,
    ExportConfig,
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
    flush_tracer,
    get_current_active_span,
    get_function_type,
    get_tracing_headers_from_current_span,
    init_tracer,
    shutdown_tracer,
)

P = ParamSpec("P")
R = TypeVar("R")


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
                async def async_generator_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
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
                            gen_func = cast(Callable[P, Generator[Any, None, None]], func)
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
]
