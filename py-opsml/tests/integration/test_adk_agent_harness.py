from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

from dev.integration.agent.agents import callbacks, pipeline
from dev.integration.agent.agents.callbacks import (
    ATTACHED_EVALS_STATE_KEY,
    FINAL_RESPONSE_STATE_KEY,
    TOOL_CALLS_STATE_KEY,
    TRIAGE_ROUTE_STATE_KEY,
    agent_output,
    attach_agent_eval,
    capture_tool_call,
)
from dev.integration.agent.agents.triage import classify_request
from dev.integration.agent.shared.setup import AgentConfig, AttachedEval


class _Span:
    trace_id = "trace-1"
    span_id = "span-1"

    def __enter__(self) -> "_Span":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def attach_eval(self, **kwargs: Any) -> None:
        self.attached_eval = kwargs

    def set_attribute(self, *_args: Any, **_kwargs: Any) -> None:
        return None


class _Tracer:
    def start_as_current_span(self, *_args: Any, **_kwargs: Any) -> _Span:
        return _Span()


class _RecordingTracer:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def start_as_current_span(self, *_args: Any, **kwargs: Any) -> _Span:
        self.calls.append(kwargs)
        return _Span()


class _SessionService:
    def __init__(self) -> None:
        self.state: dict[str, Any] | None = None

    async def create_session(self, **kwargs: Any) -> SimpleNamespace:
        self.state = kwargs["state"]
        return SimpleNamespace(id="session-1")


class _Runner:
    async def run_async(self, **_kwargs: Any) -> Any:
        event = SimpleNamespace(
            content=SimpleNamespace(parts=[SimpleNamespace(text="done")]),
            is_final_response=lambda: True,
        )
        yield event


def test_classify_request_writes_route_state() -> None:
    tool_context = SimpleNamespace(state={})

    result = classify_request("The API times out under load", tool_context)

    assert result["route"] == "timeout"
    assert tool_context.state[TRIAGE_ROUTE_STATE_KEY] == "timeout"


def test_capture_tool_call_records_state_and_returns_none() -> None:
    tool = SimpleNamespace(name="classify_request")
    tool_context = SimpleNamespace(state={})

    result = capture_tool_call(
        tool, {"query": "hello"}, tool_context, {"status": "success"}
    )

    assert result is None
    assert tool_context.state[TOOL_CALLS_STATE_KEY] == [
        {
            "name": "classify_request",
            "arguments": {"query": "hello"},
            "response": {"status": "success"},
        }
    ]


def test_agent_output_reads_public_state() -> None:
    callback_context = SimpleNamespace(state={FINAL_RESPONSE_STATE_KEY: "done"})

    assert agent_output(callback_context, FINAL_RESPONSE_STATE_KEY) == "done"


def test_agent_config_attached_eval_ledger_dedupes_and_resets() -> None:
    config = AgentConfig(app=None, prompts=None, triage=None, responder=None)  # type: ignore[arg-type]
    run_id = config.begin_run("run-1")
    attached_eval = AttachedEval(
        run_id=run_id,
        agent_name="agent",
        profile_uid="profile",
        record_id="record",
        session_id="session",
        trace_id="trace",
        span_id="span",
    )

    config.record_attached_eval(attached_eval)
    config.record_attached_eval(attached_eval)

    assert config.attached_eval_snapshot() == [attached_eval]

    config.begin_run("run-2")

    assert config.run_id == "run-2"
    assert config.attached_eval_snapshot() == []


def test_attach_agent_eval_records_config_ledger_and_state(monkeypatch) -> None:
    monkeypatch.setattr(callbacks.trace, "get_tracer", lambda _name: _Tracer())
    config = AgentConfig(app=None, prompts=None, triage=None, responder=None)  # type: ignore[arg-type]
    config.begin_run("run-1")
    callback_context = SimpleNamespace(
        state={},
        invocation_id="invocation-1",
        session=SimpleNamespace(id="session-1"),
    )

    attach_agent_eval(
        callback_context,
        config=config,
        agent_name="agent",
        profile_uid="profile",
        context={"response": "ok"},
        span_name="agent.callback",
        tracer_name="test.tracer",
    )

    [attached_eval] = config.attached_eval_snapshot()
    assert attached_eval.run_id == "run-1"
    assert attached_eval.record_id == "run-1:session-1:agent:invocation-1"
    assert callback_context.state[ATTACHED_EVALS_STATE_KEY] == [
        {
            "run_id": "run-1",
            "agent_name": "agent",
            "profile_uid": "profile",
            "record_id": "run-1:session-1:agent:invocation-1",
            "session_id": "session-1",
            "trace_id": "trace-1",
            "span_id": "span-1",
        }
    ]


def test_run_agent_turn_uses_active_span_context_not_headers(monkeypatch) -> None:
    tracer = _RecordingTracer()
    session_service = _SessionService()
    monkeypatch.setattr(pipeline.trace, "get_tracer", lambda _name: tracer)

    response = asyncio.run(
        pipeline.run_agent_turn(
            _Runner(),  # type: ignore[arg-type]
            session_service,  # type: ignore[arg-type]
            query="Help me plan dinner",
        )
    )

    assert response == "done"
    assert tracer.calls == [{}]
    assert session_service.state == {
        "temp:query": "Help me plan dinner",
        "temp:tool_calls": [],
    }
