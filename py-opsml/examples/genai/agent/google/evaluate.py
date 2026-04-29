from __future__ import annotations

import asyncio
from typing import Any

from opsml.scouter.evaluate import EvalOrchestrator, EvalScenario

from ..shared import get_shared_config, teardown
from .agent import GoogleAgentService, build_agent_service


def simulated_user_turn(
    initial_query: str,
    agent_response: Any,
    history: list[dict[str, Any]],
) -> str:
    del initial_query

    if len(history) >= 2:
        return "DONE"

    response_text = str(agent_response).lower()
    if "step" not in response_text:
        return "Give me concrete step-by-step actions and end with DONE when complete."
    return "Add one risk to watch for and then return DONE."


class GoogleInteractiveEvalOrchestrator(EvalOrchestrator):
    def __init__(self) -> None:
        config = get_shared_config()
        super().__init__(
            queue=config.app.queue,
            scenarios=config.scenarios,
            simulated_user_fn=simulated_user_turn,
        )
        self._loop = asyncio.new_event_loop()
        self._service: GoogleAgentService = build_agent_service()

    def execute_agent_turn(self, scenario: EvalScenario, message: str) -> str:
        del scenario
        return self._loop.run_until_complete(self._service.run(message))

    def close(self) -> None:
        self._loop.run_until_complete(self._service.aclose())
        pending = asyncio.all_tasks(self._loop)
        if pending:
            self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        self._loop.close()


def main() -> None:
    orchestrator = GoogleInteractiveEvalOrchestrator()
    try:
        results = orchestrator.run()
    finally:
        orchestrator.close()
        teardown()

    print(
        f"\nScenarios : {results.metrics.total_scenarios}  "
        f"Passed    : {results.metrics.passed_scenarios}  "
        f"Pass rate : {results.metrics.overall_pass_rate:.0%}"
    )
    results.as_table(show_workflow=True)


if __name__ == "__main__":
    main()
