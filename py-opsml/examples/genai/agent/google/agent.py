from __future__ import annotations

import os
from typing import Callable, Optional
from fastapi import FastAPI
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from opsml.scouter import trace
from pydantic import BaseModel

from opsml.scouter.evaluate import EvalRecord

from ..shared import get_shared_config, teardown

config = get_shared_config()
QUERY_STATE_KEY = "query"

AgentCallback = Callable[[str, str], None]


class AgentRequest(BaseModel):
    query: str


class AgentResponse(BaseModel):
    response: str


def _emit_eval_record(query: str, response: str) -> None:
    tracer = trace.get_tracer("evaluate.agent.google")
    with tracer.start_as_current_span("google.callback") as span:
        span.add_queue_item(
            "interactive_support_agent",
            EvalRecord(
                id=f"google_interactive_{abs(hash((query, response))) % 1_000_000}",
                context={"query": query, "response": response},
            ),
        )


class GoogleAgentService:
    """Owns the ADK runner and the callback used by the interactive service."""

    def __init__(self, callback: AgentCallback | None = None) -> None:
        self._callback = callback or _emit_eval_record
        self._service = self._build_service()

    def _after_model_callback(
        self,
        callback_context: CallbackContext,
        llm_response: LlmResponse,
    ) -> Optional[LlmResponse]:
        if llm_response.partial:
            return None
        if not llm_response.content or not llm_response.content.parts:
            return None

        text = next((part.text for part in llm_response.content.parts if part.text), None)
        if text:
            query = str(callback_context.state.get(QUERY_STATE_KEY, ""))
            self._callback(query, text)
        return None

    def _build_service(self) -> tuple[Runner, InMemorySessionService] | None:
        if not os.getenv("GOOGLE_API_KEY"):
            return None

        agent = Agent(
            model=config.prompt.prompt.model,
            name="google_interactive_agent",
            description="Interactive assistant",
            instruction=config.prompt.prompt.message.text,
            after_model_callback=self._after_model_callback,
        )
        session_service = InMemorySessionService()
        runner = Runner(
            agent=agent,
            app_name="opsml_google_interactive",
            session_service=session_service,
        )
        return runner, session_service

    async def aclose(self) -> None:
        if self._service is None:
            return
        runner, _ = self._service
        if hasattr(runner, "aclose"):
            await runner.aclose()
        elif hasattr(runner, "close"):
            runner.close()

    async def run(self, query: str) -> str:
        if self._service is None:
            response = self._fallback_response(query)
            self._callback(query, response)
            return response

        runner, session_service = self._service
        session = await session_service.create_session(
            app_name="opsml_google_interactive",
            user_id="evaluate_user",
            state={QUERY_STATE_KEY: query},
        )
        message = types.Content(role="user", parts=[types.Part(text=query)])
        response = ""

        event_stream = runner.run_async(
            user_id="evaluate_user",
            session_id=session.id,
            new_message=message,
        )
        try:
            async for event in event_stream:
                if event.is_final_response() and event.content:
                    parts = event.content.parts
                    if not isinstance(parts, list):
                        continue
                    for part in parts:
                        if part.text:
                            response = part.text
                            break
                    if response:
                        break
        finally:
            await event_stream.aclose()

        if not response:
            response = self._fallback_response(query)
            self._callback(query, response)
        return response

    @staticmethod
    def _fallback_response(query: str) -> str:
        lowered = query.lower()
        if "dinner" in lowered:
            return "Use one protein, one vegetable, and one starch. I can refine with your pantry."
        if "timeout" in lowered:
            return "Check timeout values, retry policy, and dependency latency."
        return "Fallback response because GOOGLE_API_KEY is not set."


def build_agent_service(callback: AgentCallback | None = None) -> GoogleAgentService:
    return GoogleAgentService(callback=callback)


_api_service = build_agent_service()

app = FastAPI(title="OpsML Google Interactive Agent")


@app.post("/ask", response_model=AgentResponse)
async def ask(request: AgentRequest) -> AgentResponse:
    response = await _api_service.run(request.query)
    return AgentResponse(response=response)


def shutdown() -> None:
    teardown()


if __name__ == "__main__":
    import argparse
    import asyncio

    _parser = argparse.ArgumentParser(description="Run Google ADK agent example.")
    _parser.add_argument("query", help="Query to send to the agent.")
    _args = _parser.parse_args()
    _service = build_agent_service()
    print(asyncio.run(_service.run(_args.query)))
    teardown()
