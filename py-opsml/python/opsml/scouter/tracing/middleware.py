# pylint: disable=missing-module-docstring
from typing import Any

from ..._opsml import SpanKind

_PROPAGATION_HEADERS = frozenset({"traceparent", "tracestate", "baggage"})
_MAX_SPAN_NAME_LEN = 512


class ScouterTracingMiddleware:
    """Raw ASGI middleware for distributed trace propagation.

    Extracts W3C ``traceparent`` context from every incoming HTTP/WebSocket
    request and starts a server-side Scouter span.  If no ``traceparent``
    header is present a new root span is created.

    Compatible with FastAPI, Starlette, and any raw ASGI server (uvicorn,
    hypercorn, etc.).  Does **not** require ``StarletteInstrumentor`` or any
    other OTel auto-instrumentor.

    When to use
    -----------
    Use this on the **receiving** side when you are **not** using
    ``StarletteInstrumentor``.  If ``StarletteInstrumentor`` is already active
    it does the same thing — do **not** use both simultaneously.

    Sending side
    ------------
    Without ``HTTPXInstrumentor``, extract headers manually and pass them to
    your HTTP client::

        with tracer.start_as_current_span("call-agent-b"):
            headers = get_tracing_headers_from_current_span()
            response = httpx.get("http://agent-b/infer", headers=headers)

    With ``HTTPXInstrumentor`` active (and ``ScouterInstrumentor.instrument()``
    called first), injection is **automatic** — no manual header extraction
    needed.

    Usage::

        from scouter.tracing import ScouterTracingMiddleware, get_tracer

        tracer = get_tracer("my-service")
        app.add_middleware(ScouterTracingMiddleware, tracer=tracer)
    """

    def __init__(self, app: Any, tracer: Any) -> None:
        self.app = app
        self.tracer = tracer

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # Extract only propagation-relevant headers; never forward credentials.
        propagation_headers: dict[str, str] = {}
        for raw_key, raw_val in scope.get("headers", []):
            key = raw_key.decode("latin-1").lower()
            if key in _PROPAGATION_HEADERS:
                try:
                    propagation_headers[key] = raw_val.decode("utf-8")
                except UnicodeDecodeError:
                    propagation_headers[key] = raw_val.decode("latin-1")

        method = scope.get("method", "")
        path = scope.get("path", "/")[:_MAX_SPAN_NAME_LEN]
        span_name = f"{method} {path}".strip() if method else path

        with self.tracer.start_as_current_span(
            span_name,
            kind=SpanKind.Server,
            headers=propagation_headers,
        ):
            await self.app(scope, receive, send)
