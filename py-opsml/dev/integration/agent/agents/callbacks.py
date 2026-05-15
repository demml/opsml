from __future__ import annotations

from dataclasses import asdict
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from opsml.scouter import trace

from ..shared import AgentConfig, AttachedEval

QUERY_STATE_KEY = "temp:query"
TOOL_CALLS_STATE_KEY = "temp:tool_calls"
TRIAGE_ROUTE_STATE_KEY = "temp:triage_route"
TRIAGE_RESPONSE_STATE_KEY = "temp:triage_response"
FINAL_RESPONSE_STATE_KEY = "temp:final_response"
ATTACHED_EVALS_STATE_KEY = "temp:attached_evals"


def capture_tool_call(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict[str, Any],
) -> dict[str, Any] | None:
    tool_calls = list(tool_context.state.get(TOOL_CALLS_STATE_KEY, []))
    tool_calls.append(
        {
            "name": tool.name,
            "arguments": args,
            "response": tool_response,
        }
    )
    tool_context.state[TOOL_CALLS_STATE_KEY] = tool_calls
    return None


def tool_call_names(callback_context: CallbackContext) -> list[str]:
    tool_calls = list(callback_context.state.get(TOOL_CALLS_STATE_KEY, []))
    return [str(call.get("name", "")) for call in tool_calls]


def tool_results(callback_context: CallbackContext) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for call in callback_context.state.get(TOOL_CALLS_STATE_KEY, []):
        if isinstance(call, dict) and isinstance(call.get("response"), dict):
            results[str(call["name"])] = call["response"]
    return results


def agent_output(callback_context: CallbackContext, state_key: str) -> str:
    return str(callback_context.state.get(state_key, ""))


def session_id(callback_context: CallbackContext) -> str:
    session = getattr(callback_context, "session", None)
    if session is not None:
        return str(getattr(session, "id", ""))
    return ""


def record_id(
    callback_context: CallbackContext,
    agent_name: str,
    *,
    run_id: str = "",
    session_id_value: str = "",
) -> str:
    return ":".join(
        part
        for part in [
            run_id,
            session_id_value,
            agent_name,
            str(callback_context.invocation_id),
        ]
        if part
    )


def attach_agent_eval(
    callback_context: CallbackContext,
    *,
    config: AgentConfig,
    agent_name: str,
    profile_uid: str,
    context: dict[str, Any],
    span_name: str,
    tracer_name: str,
) -> None:
    tracer = trace.get_tracer(tracer_name)
    state = callback_context.state
    with tracer.start_as_current_span(span_name) as span:
        attached_session_id = session_id(callback_context)
        attached_record_id = record_id(
            callback_context,
            agent_name,
            run_id=config.run_id,
            session_id_value=attached_session_id,
        )
        span.attach_eval(
            profile_uid=profile_uid,
            context=context,
            record_id=attached_record_id,
            session_id=attached_session_id,
            tags=[
                "source=google_adk",
                f"agent={agent_name}",
                f"run_id={config.run_id}",
            ],
        )
        attached_eval = AttachedEval(
            run_id=config.run_id,
            agent_name=agent_name,
            profile_uid=profile_uid,
            record_id=attached_record_id,
            session_id=attached_session_id,
            trace_id=span.trace_id,
            span_id=span.span_id,
        )
        evals = list(state.get(ATTACHED_EVALS_STATE_KEY, []))
        evals.append(asdict(attached_eval))
        state[ATTACHED_EVALS_STATE_KEY] = evals
        config.record_attached_eval(attached_eval)
