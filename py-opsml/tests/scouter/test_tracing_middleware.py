import asyncio
from contextlib import contextmanager

from opsml.scouter.tracing.middleware import ScouterTracingMiddleware


class DummyTracer:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    @contextmanager
    def start_as_current_span(self, name: str, kind: object, headers: dict[str, str]):
        self.calls.append({"name": name, "kind": kind, "headers": headers})
        yield


async def _asgi_ok_app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"ok", "more_body": False})


def _run_middleware(headers: list[tuple[bytes, bytes]]) -> DummyTracer:
    tracer = DummyTracer()
    middleware = ScouterTracingMiddleware(_asgi_ok_app, tracer=tracer)
    scope = {"type": "http", "method": "GET", "path": "/health", "headers": headers}

    events = [
        {"type": "http.request", "body": b"", "more_body": False},
    ]

    async def receive():
        if events:
            return events.pop(0)
        return {"type": "http.disconnect"}

    async def send(_message):
        return

    asyncio.run(middleware(scope, receive, send))
    return tracer


def test_tracing_middleware_strips_reserved_scouter_baggage_keys():
    tracer = _run_middleware(
        [
            (b"traceparent", b"00-1234567890abcdef1234567890abcdef-1234567890abcdef-01"),
            (b"baggage", b"scouter.active.entity_uid=spoofed,user.id=123,team=ml"),
        ]
    )

    headers = tracer.calls[0]["headers"]
    assert isinstance(headers, dict)
    assert headers["baggage"] == "user.id=123, team=ml"
    assert "traceparent" in headers


def test_tracing_middleware_drops_baggage_when_only_reserved_entries():
    tracer = _run_middleware(
        [
            (b"traceparent", b"00-1234567890abcdef1234567890abcdef-1234567890abcdef-01"),
            (b"baggage", b"scouter.active.entity_uid=spoofed"),
        ]
    )

    headers = tracer.calls[0]["headers"]
    assert isinstance(headers, dict)
    assert "baggage" not in headers
