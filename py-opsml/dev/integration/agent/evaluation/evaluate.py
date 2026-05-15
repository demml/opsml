from __future__ import annotations

import argparse
import asyncio
import contextvars
from collections.abc import Coroutine
from pathlib import Path
from typing import Any

from opsml.scouter.evaluate import (
    EvalOrchestrator,
    EvalScenario,
    EvalScenarios,
    ScenarioEvalResults,
)
from opsml.scouter.transport import MockConfig

from ..agents import build_runner, run_agent_turn
from ..shared import get_shared_config, teardown
from .user_agent import SimulatedUserAgent

_SCENARIOS_PATH = Path(__file__).resolve().parent.parent / "shared" / "scenarios.jsonl"


class GoogleAdkEvalOrchestrator(EvalOrchestrator):
    def __init__(self) -> None:
        self._config = get_shared_config(transport_config=MockConfig(), register=False)
        self._config.begin_run()
        self._runner = asyncio.Runner()
        self._sim_user = SimulatedUserAgent(
            config=self._config, run_sync=self._run_sync
        )
        self._adk_runner, self._session_service = build_runner(self._config)
        super().__init__(
            queue=self._config.app.queue,
            scenarios=EvalScenarios.from_path(_SCENARIOS_PATH),
            simulated_user_fn=self._sim_user.turn_factory("__default__"),
        )

    def _run_sync(self, coro: Coroutine[Any, Any, str]) -> str:
        return self._runner.run(coro, context=contextvars.copy_context())

    def execute_agent_turn(self, scenario: EvalScenario, message: str) -> str:
        self._simulated_user_fn = self._sim_user.turn_factory(scenario.id)
        return self._run_sync(
            run_agent_turn(
                self._adk_runner,
                self._session_service,
                query=message,
                user_id="eval_user",
            )
        )

    def close(self) -> None:
        self._sim_user.close()
        self._runner.close()


def run_offline_evaluation() -> ScenarioEvalResults:
    orchestrator = GoogleAdkEvalOrchestrator()
    try:
        return orchestrator.run()
    finally:
        orchestrator.close()
        teardown()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run offline ADK agent evaluation.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if any offline evaluation scenario fails.",
    )
    args = parser.parse_args()

    results = run_offline_evaluation()
    print(
        f"\nScenarios : {results.metrics.total_scenarios}  "
        f"Passed    : {results.metrics.passed_scenarios}  "
        f"Pass rate : {results.metrics.overall_pass_rate:.0%}"
    )
    results.as_table(show_workflow=True)
    results.agent_summary_table()

    print("\nDetail for 'plan_weeknight_dinner':")
    detail = results.get_scenario_detail("plan_weeknight_dinner")
    detail.traces_as_table()
    detail.tasks_as_table()
    detail.agent_results_as_table(show_tasks=True)

    print("Spans --------------------------------")
    spans = detail.traces
    for span in spans:
        print(
            "parent:",
            span.parent_span_id,
            "id:",
            span.span_id,
            "name:",
            span.span_name,
            "depth:",
            span.depth,
        )
    print("-------------------------------------")

    if (
        args.check
        and results.metrics.passed_scenarios != results.metrics.total_scenarios
    ):
        raise SystemExit(
            "Offline evaluation failed: "
            f"{results.metrics.passed_scenarios}/"
            f"{results.metrics.total_scenarios} scenarios passed"
        )

    print("\nDetail for 'debug_api_timeout':")
    detail = results.get_scenario_detail("debug_api_timeout")
    detail.traces_as_table()
    detail.tasks_as_table()
    detail.agent_results_as_table(show_tasks=True)


if __name__ == "__main__":
    main()
