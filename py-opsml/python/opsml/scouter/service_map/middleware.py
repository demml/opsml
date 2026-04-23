from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from ..._opsml import (
    GrpcConfig,
    py_extract_trace_id,
    py_infer_schema,
    py_normalize_endpoint,
)
from ..bifrost import Bifrost, TableConfig, WriteConfig

# Aliased so existing imports like `from .middleware import _normalize_endpoint` continue to work.
_normalize_endpoint = py_normalize_endpoint
_extract_trace_id = py_extract_trace_id
_infer_schema = py_infer_schema

SERVICE_MAP_CATALOG = "scouter"
SERVICE_MAP_SCHEMA = "service_map"
SERVICE_MAP_TABLE = "connections"


class ServiceConnectionRecord(BaseModel):
    source_service: str = Field(max_length=256)
    destination_service: str
    endpoint: str
    method: str
    status_code: int
    latency_ms: float
    timestamp: datetime
    trace_id: Optional[str] = None
    error: bool
    source_verified: bool = False  # True when identity is cryptographically verified (e.g. mTLS)
    tags: Optional[str] = None  # JSON-encoded {key: value} user-defined metadata
    request_schema: Optional[str] = None  # JSON-encoded {field_name: json_type}


async def _buffer_body(receive: Any, max_bytes: int) -> tuple[bytes, Any]:
    messages: list[Any] = []
    chunks: list[bytes] = []
    total = 0
    exceeded = False

    while True:
        msg = await receive()
        messages.append(msg)
        if msg["type"] == "http.disconnect":
            break
        if msg["type"] == "http.request":
            chunk = msg.get("body", b"")
            if chunk:
                total += len(chunk)
                if total > max_bytes:
                    exceeded = True
                    break
                chunks.append(chunk)
            if not msg.get("more_body", False):
                break

    body = b"" if exceeded else b"".join(chunks)
    idx = 0

    async def replay() -> Any:
        nonlocal idx
        if idx < len(messages):
            m = messages[idx]
            idx += 1
            return m
        return await receive()

    return body, replay


class ServiceMapMiddleware:
    """ASGI middleware that records service-to-service connection events into Bifrost.

    Each incoming HTTP request produces a ``ServiceConnectionRecord`` that is
    buffered and flushed asynchronously to the scouter server via gRPC.

    Designed to stack with ``ScouterTracingMiddleware`` — when placed as the
    inner middleware, it reads the active OTel trace ID from the current span
    context automatically:

    .. code-block:: python

        app.add_middleware(ServiceMapMiddleware, ...)       # inner
        app.add_middleware(ScouterTracingMiddleware, ...)   # outer

    When used standalone (no tracing middleware), falls back to parsing the
    ``traceparent`` header directly.

    Note: ``source_service`` is an untrusted hint from the ``x-scouter-service``
    header — any caller can set it to any value. Use ``source_verified`` to
    distinguish authenticated identities (e.g. mTLS) from header-based ones.

    Args:
        app: The ASGI application to wrap.
        grpc_address: Scouter server gRPC address, e.g. ``"scouter:50051"``.
        service_name: This service's identity (used as ``destination_service``).
        tags: Optional key-value metadata stamped on every connection record,
            e.g. ``{"env": "prod", "region": "us-east-1"}``. Queryable via
            ``json_extract(tags, '$.env')`` in DataFusion SQL.
        capture_schema: If ``True``, inspect incoming JSON request bodies and
            record top-level field names + inferred JSON types in
            ``request_schema``. Schema inference reads top-level field names and
            types only; the full body must fit within ``max_body_bytes`` to
            capture schema. For routes with very large payloads where schema is
            already known, set ``capture_schema=False``.
        max_body_bytes: Maximum body size to buffer when ``capture_schema=True``
            (default: 16 MB). If the body exceeds this limit, schema capture is
            silently skipped for that request.
        batch_size: Number of records before forcing a flush (default: 100).
        flush_interval_secs: Seconds between scheduled background flushes (default: 5).
    """

    def __init__(
        self,
        app: Any,
        grpc_address: str,
        service_name: str,
        tags: Optional[dict[str, str]] = None,
        capture_schema: bool = False,
        max_body_bytes: int = 16_777_216,
        batch_size: int = 100,
        flush_interval_secs: int = 5,
    ) -> None:
        self.app = app
        self._service_name = service_name
        self._tags_json: Optional[str] = json.dumps(tags) if tags else None
        self._capture_schema = capture_schema
        self._max_body_bytes = max_body_bytes
        self._bifrost = Bifrost(
            table_config=TableConfig(
                model=ServiceConnectionRecord,
                catalog=SERVICE_MAP_CATALOG,
                schema_name=SERVICE_MAP_SCHEMA,
                table=SERVICE_MAP_TABLE,
            ),
            transport=GrpcConfig(server_uri=grpc_address),
            write_config=WriteConfig(
                batch_size=batch_size,
                scheduled_delay_secs=flush_interval_secs,
            ),
        )

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers: dict[str, str] = {}
        for raw_key, raw_val in scope.get("headers", []):
            key = raw_key.decode("latin-1").lower()
            try:
                headers[key] = raw_val.decode("utf-8")
            except UnicodeDecodeError:
                headers[key] = raw_val.decode("latin-1")

        source_service = headers.get("x-scouter-service", "unknown")[:256]

        # Prefer active OTel span; fall back to traceparent header
        trace_id: Optional[str] = None
        try:
            from opentelemetry import (
                trace as otel_trace,  # type: ignore[import-untyped]
            )

            ctx = otel_trace.get_current_span().get_span_context()
            if ctx.is_valid:
                trace_id = format(ctx.trace_id, "032x")
        except ImportError:
            pass

        if trace_id is None:
            tp = headers.get("traceparent")
            if tp:
                trace_id = _extract_trace_id(tp)

        method = scope.get("method", "")
        endpoint = _normalize_endpoint(scope.get("path", "/"))

        request_schema: Optional[str] = None
        content_type = headers.get("content-type", "")
        if self._capture_schema and content_type.startswith("application/json"):
            content_length = headers.get("content-length")
            try:
                skip = content_length is not None and int(content_length) > self._max_body_bytes
            except (ValueError, OverflowError):
                skip = False
            if not skip:
                body, receive = await _buffer_body(receive, self._max_body_bytes)
                if body:
                    request_schema = _infer_schema(body)

        status_holder: list[int] = [200]

        async def send_wrapper(message: Any) -> None:
            if message["type"] == "http.response.start":
                status_holder[0] = message.get("status", 200)
            await send(message)

        # start timer after optional body buffer; latency_ms measures server processing time only
        start = time.monotonic()
        await self.app(scope, receive, send_wrapper)
        latency_ms = (time.monotonic() - start) * 1000.0

        status_code = status_holder[0]
        self._bifrost.insert(
            ServiceConnectionRecord(
                source_service=source_service,
                destination_service=self._service_name,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                latency_ms=round(latency_ms, 3),
                timestamp=datetime.now(timezone.utc),
                trace_id=trace_id,
                error=status_code >= 500,
                source_verified=False,
                tags=self._tags_json,
                request_schema=request_schema,
            )
        )
