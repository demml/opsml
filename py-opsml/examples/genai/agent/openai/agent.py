from __future__ import annotations

import os
from typing import Any, Callable

from agents import Agent, RunHooks, Runner
from fastapi import FastAPI
from pydantic import BaseModel
from opsml.scouter import trace
from opsml.scouter.evaluate import EvalRecord

from ..shared import get_shared_config, teardown

config = get_shared_config()

AgentCallback = Callable[[str, str], None]


class AgentRequest(BaseModel):
    query: str


class AgentResponse(BaseModel):
    response: str


def _emit_eval_record(query: str, response: str) -> None:
    tracer = trace.get_tracer("evaluate.agent.openai")
    with tracer.start_as_current_span("openai.callback") as span:
        span.add_queue_item(
            "interactive_support_agent",
            EvalRecord(
                id=f"openai_interactive_{abs(hash((query, response))) % 1_000_000}",
                context={"query": query, "response": response},
            ),
        )


def _fallback_response(query: str) -> str:
    lowered = query.lower()
    if "dinner" in lowered:
        return "Use one protein, one vegetable, and one starch. Add quick prep and cook steps."
    if "timeout" in lowered:
        return "Inspect timeout configuration, retries, and dependency latency first."
    return "Fallback response because OPENAI_API_KEY is not set."


def run_agent(query: str, callback: AgentCallback | None = None) -> str:
    on_response = callback or _emit_eval_record

    if not os.getenv("OPENAI_API_KEY"):
        response = _fallback_response(query)
        on_response(query, response)
        return response

    class EvalHooks(RunHooks[Any]):
        def __init__(self, query: str, callback: AgentCallback) -> None:
            self._query = query
            self._callback = callback

        async def on_agent_end(self, context: Any, agent: Any, output: Any) -> None:
            del context
            del agent
            self._callback(self._query, str(output))

    agent = Agent(
        name="openai_interactive_agent",
        instructions=config.prompt.prompt.message.text,
        model="gpt-4.1-mini",
    )

    with trace.get_tracer("evaluate.agent.openai").start_as_current_span("openai.agent.run"):
        result = Runner.run_sync(agent, query, hooks=EvalHooks(query=query, callback=on_response))
    return str(result.final_output)


app = FastAPI(title="OpsML OpenAI Interactive Agent")


@app.post("/ask", response_model=AgentResponse)
def ask(request: AgentRequest) -> AgentResponse:
    return AgentResponse(response=run_agent(request.query))


def shutdown() -> None:
    teardown()
