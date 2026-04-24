from opsml.scouter.evaluate import EvalOrchestrator

from ..shared import get_shared_config, teardown
from .agent import run_agent


def simulated_user_turn(initial_query: str, agent_response: str, history: list[dict[str, str]]) -> str:
    del initial_query

    if len(history) >= 2:
        return "DONE"
    if "step" not in str(agent_response).lower():
        return "Give concrete steps and then return DONE."
    return "Add one failure mode and return DONE."


def main() -> None:
    config = get_shared_config()
    try:
        results = EvalOrchestrator(
            queue=config.app.queue,
            scenarios=config.scenarios,
            agent_fn=run_agent,
            simulated_user_fn=simulated_user_turn,
        ).run()
    finally:
        teardown()

    print(
        f"\nScenarios : {results.metrics.total_scenarios}  "
        f"Passed    : {results.metrics.passed_scenarios}  "
        f"Pass rate : {results.metrics.overall_pass_rate:.0%}"
    )
    results.as_table(show_workflow=True)


if __name__ == "__main__":
    main()
