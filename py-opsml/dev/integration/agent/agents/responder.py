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
    FINAL_RESPONSE_STATE_KEY,
    QUERY_STATE_KEY,
    TOOL_CALLS_STATE_KEY,
    TRIAGE_ROUTE_STATE_KEY,
    agent_output,
    attach_agent_eval,
    capture_tool_call,
    tool_call_names,
    tool_results,
)

RESPONDER_AGENT_NAME = "responder_agent"


def plan_weeknight_dinner(query: str, tool_context: ToolContext) -> dict[str, Any]:
    """Build a simple weeknight dinner plan for dinner-routed requests."""
    tracer = trace.get_tracer("opsml_e2e_agent.tools")
    with tracer.start_as_current_span("tool.plan_weeknight_dinner") as span:
        span.set_attribute("tool.name", "plan_weeknight_dinner")
        span.set_attribute("tool.query", query)
        return {
            "status": "success",
            "route": "dinner",
            "query": query,
            "ingredients": ["protein", "vegetable", "starch"],
            "next_step": "Choose one ingredient from each category, then build a short prep sequence.",
        }


def debug_api_timeout(query: str, tool_context: ToolContext) -> dict[str, Any]:
    """Return focused troubleshooting checks for timeout-routed requests."""
    tracer = trace.get_tracer("opsml_e2e_agent.tools")
    with tracer.start_as_current_span("tool.debug_api_timeout") as span:
        span.set_attribute("tool.name", "debug_api_timeout")
        span.set_attribute("tool.query", query)
        return {
            "status": "success",
            "route": "timeout",
            "query": query,
            "checks": ["timeout values", "retry policy", "dependency latency"],
            "next_step": "Check timeout values, retry policy, and dependency latency.",
        }


def build_responder_agent(config: AgentConfig | None = None) -> Agent:
    active_config = config or get_shared_config()

    def instruction(context: ReadonlyContext) -> str:
        query = context.state.get(QUERY_STATE_KEY, "")
        triage_route = context.state.get(TRIAGE_ROUTE_STATE_KEY, "")
        return "\n\n".join(
            [
                active_config.prompts.responder.prompt.message.text,
                f"Current user query: {query}",
                f"Triage route: {triage_route}",
                (
                    "Use the triage route to choose one tool: plan_weeknight_dinner "
                    "for route 'dinner', or debug_api_timeout for route 'timeout'. "
                    "Call exactly one route tool and do not transfer to another agent."
                ),
            ]
        )

    return Agent(
        name=RESPONDER_AGENT_NAME,
        model=active_config.prompts.responder.prompt.model,
        description="Calls the routed domain tool and produces the final answer.",
        instruction=instruction,
        output_key=FINAL_RESPONSE_STATE_KEY,
        tools=[plan_weeknight_dinner, debug_api_timeout],
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
        after_tool_callback=capture_tool_call,
        after_agent_callback=lambda callback_context: _after_responder_agent(
            callback_context,
            active_config,
        ),
    )


def _after_responder_agent(
    callback_context: CallbackContext,
    config: AgentConfig,
) -> types.Content | None:
    state = callback_context.state
    names = tool_call_names(callback_context)
    results = tool_results(callback_context)
    response = agent_output(callback_context, FINAL_RESPONSE_STATE_KEY)
    if not response:
        response = next(
            (
                str(result.get("next_step", ""))
                for name, result in results.items()
                if name in {"plan_weeknight_dinner", "debug_api_timeout"}
                and isinstance(result, dict)
            ),
            "",
        )
        state[FINAL_RESPONSE_STATE_KEY] = response

    context = {
        "query": str(state.get(QUERY_STATE_KEY, "")),
        "response": response,
        "final_response": response,
        "tool_call_names": names,
        "tool_call_path": " -> ".join(names),
        "tool_call_trajectory": " -> ".join(names),
        "tool_calls": list(state.get(TOOL_CALLS_STATE_KEY, [])),
        "tool_results": results,
        "triage_route": str(state.get(TRIAGE_ROUTE_STATE_KEY, "")),
    }

    attach_agent_eval(
        callback_context,
        config=config,
        agent_name=RESPONDER_AGENT_NAME,
        profile_uid=config.responder.eval_profile.config.uid,
        context=context,
        span_name="responder.callback",
        tracer_name="opsml_e2e_agent.responder",
    )

    return None
