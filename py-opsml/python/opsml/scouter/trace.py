"""Scouter-aware proxy for ``opentelemetry.trace``."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from opentelemetry.trace import Span as OTelSpan
    from opentelemetry.trace import TracerProvider as OTelTracerProvider

    from ..scouter.tracing import ScouterTracer

_otel_trace: ModuleType | None = None

try:
    _otel_trace = import_module("opentelemetry.trace")
except ImportError:
    pass

if _otel_trace is not None:
    Span = _otel_trace.Span
    SpanKind = _otel_trace.SpanKind
    Tracer = _otel_trace.Tracer


def _require_opentelemetry() -> ModuleType:
    if _otel_trace is None:
        msg = "opentelemetry-api is not installed. Install with: pip install scouter-ml[opentelemetry]"
        raise ImportError(msg)
    return _otel_trace


def __getattr__(name: str) -> object:
    if name == "get_tracer":
        return get_tracer
    return getattr(_require_opentelemetry(), name)


def __dir__() -> list[str]:
    names = set(globals())
    if _otel_trace is not None:
        names.update(dir(_otel_trace))
    return sorted(names)


def get_tracer(
    instrumenting_module_name: str,
    instrumenting_library_version: Optional[str] = None,  # noqa: ARG001
    schema_url: Optional[str] = None,  # noqa: ARG001
) -> ScouterTracer:
    """Return a Scouter tracer from the global OpenTelemetry provider."""
    _require_opentelemetry()
    from ..scouter.tracing import (
        get_tracer as _get_tracer,  # pylint: disable=import-outside-toplevel
    )

    return _get_tracer(instrumenting_module_name)


def get_tracer_provider() -> OTelTracerProvider:
    """Return the global OpenTelemetry tracer provider."""
    return _require_opentelemetry().get_tracer_provider()


def set_tracer_provider(provider: Any) -> None:
    """Set the global OpenTelemetry tracer provider."""
    _require_opentelemetry().set_tracer_provider(provider)


def get_current_span(context: Any = None) -> OTelSpan:
    """Return the current OpenTelemetry span."""
    return _require_opentelemetry().get_current_span(context)


def use_span(*args: Any, **kwargs: Any) -> Any:
    """Proxy to OpenTelemetry's span context manager helper."""
    return _require_opentelemetry().use_span(*args, **kwargs)


__all__ = [
    "Span",
    "SpanKind",
    "Tracer",
    "get_current_span",
    "get_tracer",
    "get_tracer_provider",
    "set_tracer_provider",
    "use_span",
]
