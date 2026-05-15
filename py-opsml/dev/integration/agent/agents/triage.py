from __future__ import annotations

from typing import Any

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from opsml.scouter import trace

from ..shared import AgentConfig, get_shared_config
from .callbacks import (
    QUERY_STATE_KEY,
    TOOL_CALLS_STATE_KEY,
    TRIAGE_ROUTE_STATE_KEY,
    TRIAGE_RESPONSE_STATE_KEY,
    agent_output,
    attach_agent_eval,
    capture_tool_call,
    tool_call_names,
    tool_results,
)

TRIAGE_AGENT_NAME = "triage_agent"


def classify_request(query: str, tool_context: ToolContext) -> dict[str, Any]:
    """Classify the support request into the route used by the responder."""
    tracer = trace.get_tracer("opsml_e2e_agent.tools")
    lowered = query.lower()
    route = "timeout" if "timeout" in lowered or "times out" in lowered else "dinner"
    tool_context.state[TRIAGE_ROUTE_STATE_KEY] = route
    with tracer.start_as_current_span("tool.classify_request") as span:
        span.set_attribute("tool.name", "classify_request")
        span.set_attribute("tool.query", query)
        span.set_attribute("tool.route", route)
        return {"status": "success", "query": query, "route": route}


def build_triage_agent(config: AgentConfig | None = None) -> Agent:
    active_config = config or get_shared_config()

    def instruction(context: ReadonlyContext) -> str:
        query = context.state.get(QUERY_STATE_KEY, "")
        return "\n\n".join(
            [
                active_config.prompts.triage.prompt.message.text,
                f"Current user query: {query}",
                "Call classify_request exactly once. Do not transfer to another agent.",
            ]
        )

    return Agent(
        name=TRIAGE_AGENT_NAME,
        model=active_config.prompts.triage.prompt.model,
        description="Classifies the user request into the next support route.",
        instruction=instruction,
        output_key=TRIAGE_RESPONSE_STATE_KEY,
        tools=[classify_request],
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
        after_tool_callback=capture_tool_call,
        after_agent_callback=lambda callback_context: _after_triage_agent(
            callback_context,
            active_config,
        ),
    )


def _after_triage_agent(
    callback_context: CallbackContext,
    config: AgentConfig,
) -> types.Content | None:
    state = callback_context.state
    results = tool_results(callback_context)
    triage_route = str(state.get(TRIAGE_ROUTE_STATE_KEY, ""))

    names = tool_call_names(callback_context)
    response = agent_output(callback_context, TRIAGE_RESPONSE_STATE_KEY)
    if not response and triage_route:
        response = f"The request is routed to {triage_route}."
    context = {
        "query": str(state.get(QUERY_STATE_KEY, "")),
        "response": response,
        "tool_call_names": names,
        "tool_call_path": " -> ".join(names),
        "tool_call_trajectory": " -> ".join(names),
        "tool_calls": list(state.get(TOOL_CALLS_STATE_KEY, [])),
        "tool_results": results,
        "triage_route": triage_route,
    }

    attach_agent_eval(
        callback_context,
        config=config,
        agent_name=TRIAGE_AGENT_NAME,
        profile_uid=config.triage.eval_profile.config.uid,
        context=context,
        span_name="triage.callback",
        tracer_name="opsml_e2e_agent.triage",
    )

    return None
