from __future__ import annotations

import asyncio

from google.adk.agents import SequentialAgent
from google.adk.runners import Runner, RunConfig
from google.adk.sessions import InMemorySessionService
from google.genai import types
from opsml.scouter import trace

from ..shared import APP_NAME, AgentConfig, get_shared_config
from .callbacks import (
    QUERY_STATE_KEY,
    TOOL_CALLS_STATE_KEY,
)
from .responder import build_responder_agent
from .triage import build_triage_agent

ROOT_AGENT_NAME = "opsml_e2e_support_pipeline"
# Expected path is 4 LLM calls. Budget 6 allows one repair turn without masking loops.
MAX_LLM_CALLS_PER_TURN = 6


def build_root_agent(config: AgentConfig | None = None) -> SequentialAgent:
    active_config = config or get_shared_config()
    return SequentialAgent(
        name=ROOT_AGENT_NAME,
        sub_agents=[
            build_triage_agent(active_config),
            build_responder_agent(active_config),
        ],
    )


def build_runner(
    config: AgentConfig | None = None,
) -> tuple[Runner, InMemorySessionService]:
    active_config = config or get_shared_config()
    session_service = InMemorySessionService()
    runner = Runner(
        agent=build_root_agent(active_config),
        app_name=APP_NAME,
        session_service=session_service,
    )
    return runner, session_service


async def run_agent_turn(
    runner: Runner,
    session_service: InMemorySessionService,
    *,
    query: str,
    user_id: str = "e2e_user",
) -> str:
    tracer = trace.get_tracer("opsml_e2e_agent.request")
    response = ""
    with tracer.start_as_current_span("agent.request") as span:
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            state={
                QUERY_STATE_KEY: query,
                TOOL_CALLS_STATE_KEY: [],
            },
        )
        message = types.Content(role="user", parts=[types.Part(text=query)])
        span.set_attribute("adk.session_id", session.id)
        span.set_attribute("adk.user_id", user_id)
        span.set_attribute("agent.query", query)
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=message,
            run_config=RunConfig(max_llm_calls=MAX_LLM_CALLS_PER_TURN),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                response = "".join(part.text or "" for part in event.content.parts)

    return response


def run_query(query: str) -> str:
    config = get_shared_config()
    config.begin_run()
    runner, session_service = build_runner(config)
    return asyncio.run(run_agent_turn(runner, session_service, query=query))
