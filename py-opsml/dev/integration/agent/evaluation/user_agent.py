from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ..shared import AgentConfig

_SIM_USER_NAME = "simulated_user"
_SIM_USER_APP_NAME = "opsml_e2e_simulated_user"


def _instruction(persona: str) -> str:
    return (
        f"You are simulating a user with this persona: {persona}.\n"
        "Read the conversation history. Reply as the user would in one short paragraph.\n"
        "When the agent's most recent answer fully addresses your goal, end your reply with DONE.\n"
        "If you still need clarification or a follow-up, do not include DONE.\n"
    )


class SimulatedUserAgent:
    def __init__(
        self,
        config: AgentConfig,
        persona: str = "a curious data scientist",
        *,
        run_sync: Callable[[Coroutine[Any, Any, str]], str] | None = None,
    ) -> None:
        self._agent = Agent(
            name=_SIM_USER_NAME,
            model=config.prompts.responder.prompt.model,
            description="Simulates a user driving the agent under evaluation.",
            instruction=_instruction(persona),
        )
        self._session_service = InMemorySessionService()
        self._runner = Runner(
            agent=self._agent,
            app_name=_SIM_USER_APP_NAME,
            session_service=self._session_service,
        )
        if run_sync:
            self._owned_async_runner = None
            self._run_sync = run_sync
        else:
            self._owned_async_runner = asyncio.Runner()
            self._run_sync = self._owned_async_runner.run
        self._sessions: dict[str, str] = {}

    async def _ensure_session(self, scenario_id: str) -> str:
        if scenario_id in self._sessions:
            return self._sessions[scenario_id]
        session = await self._session_service.create_session(
            app_name=_SIM_USER_APP_NAME,
            user_id=f"sim_user::{scenario_id}",
            state={},
        )
        self._sessions[scenario_id] = session.id
        return session.id

    async def _turn_async(self, scenario_id: str, agent_response: Any) -> str:
        session_id = await self._ensure_session(scenario_id)
        message = types.Content(
            role="user", parts=[types.Part(text=str(agent_response))]
        )
        last_text = ""
        try:
            async for event in self._runner.run_async(
                user_id=f"sim_user::{scenario_id}",
                session_id=session_id,
                new_message=message,
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            last_text = part.text
        except Exception:
            return "DONE"
        return last_text or "DONE"

    def turn_factory(
        self, scenario_id: str
    ) -> Callable[[str, Any, list[dict[str, Any]]], str]:
        def _turn(
            initial_query: str,
            agent_response: Any,
            history: list[dict[str, Any]],
        ) -> str:
            del initial_query, history
            return self._run_sync(self._turn_async(scenario_id, agent_response))

        return _turn

    def close(self) -> None:
        if self._owned_async_runner:
            self._owned_async_runner.close()
